from app.models.models import Order, Client, Item, Categoria, Estado
from flask import Blueprint, render_template,request, redirect, url_for, jsonify, make_response, Response, flash
from flask_login import login_required, current_user
from sqlalchemy import text, cast, desc
from app import db
from decimal import Decimal
from datetime import datetime
import math, uuid, pdfkit, re, json
import logging
from flask import current_app



# Configure o sistema de logging
logging.basicConfig(level=logging.DEBUG)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    total_ordens = Order.query.count()
    ordens_concluidas = Order.query.filter_by(status='Concluida').count()
    ordens_canceladas = Order.query.filter_by(status='Cancelada').count()
    # Lógica para exibir o dashboard
    return render_template('/dash/dashboard.html', email=current_user.email,total_ordens=total_ordens,
                        ordens_concluidas=ordens_concluidas,ordens_canceladas=ordens_canceladas)

##################### Formulario de ORDENS #########################
@dashboard_bp.route('/ordem_form')
@login_required
def ordem_form():
    order = Order.query.all()
    order_count_plus_one = len(order) + 1
    
    clientes = Client.query.order_by(Client.nome).all()
    itens = Item.query.all()  # Consulta para obter todos os itens
    categorias = Categoria.query.all()
    estados = Estado.query.all()
    
    opcoes_pagamento = ["Transferência bancária", "Link de pagamento", "Cartão de crédito", 
                        "Cartão de débito", "Pix", "Boleto bancário", "Dinheiro em espécie"]
    
    # Renderize o template e passe o número de ordem como contexto
    return render_template('/ordens/ordem_form.html',opcoes_pagamento=opcoes_pagamento, email=current_user.email,
                        order=order, order_count_plus_one=order_count_plus_one, clientes=clientes, itens=itens,categorias=categorias,
                        estados=estados)


@dashboard_bp.route('/salvar_ordem', methods=['POST'])
@login_required
def salvar_ordem():
    if request.method == 'POST':
        # Verificar se todos os campos necessários estão presentes no formulário
        required_fields = ['data_inicio', 'prev_entrega', 'cliente', 'equipamento', 'forma_pagamento', 'prioridade', 'status', 'observacoes', 'categoria', 'items', 'valor_total']
        for field in required_fields:
            if field not in request.form:
                return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400

        total_ordens = Order.query.count()
        
        operador = current_user.first_name + ' ' + current_user.last_name
        data_inicio = request.form['data_inicio']
        previsao_entrega = request.form['prev_entrega']
        cliente_id = request.form['cliente']
        cliente = Client.query.get(cliente_id)
        nome_cliente = cliente.nome if cliente else None
        equipamento = request.form['equipamento']
        forma_pagamento = request.form['forma_pagamento']
        prioridade = request.form['prioridade']
        status = request.form['status']
        observacoes = request.form['observacoes']
        categoria_ordem = request.form['categoria']  # Adicionando categoria_ordem
        next_order_number = total_ordens + 1
        items_json = request.form['items']
        items = json.loads(items_json)
        
        # Verificar se o campo 'valor_total' está presente e é um número válido
        if 'valor_total' not in request.form:
            return jsonify({'error': 'Campo "valor_total" ausente no formulário'}), 400
        try:
            valor_total_ordem = float(request.form['valor_total'])
        except ValueError:
            return jsonify({'error': 'O campo "valor_total" não é um número válido'}), 400


        # Crie a ordem após adicionar os itens para obter o ID da ordem
        nova_ordem = Order(
            numero_ordem=str(next_order_number),
            operador=operador, 
            data_inicio=data_inicio, 
            previsao_entrega=previsao_entrega,
            cliente=nome_cliente, 
            equipamento=equipamento, 
            forma_pagamento=forma_pagamento,
            prioridade=prioridade, 
            status=status,
            observacoes=observacoes,
            categoria_ordem=categoria_ordem, 
            valor_total=valor_total_ordem,
            items=items
        )

        db.session.add(nova_ordem)
        db.session.commit()

        return redirect(url_for('dashboard.ordens', valor_total=valor_total_ordem, ordem_id=nova_ordem.id))

##################### Gerenciamento de ORDENS #########################
@dashboard_bp.route('/ordens')
@login_required
def ordens():
    # Página atual e número de itens por página
    page = request.args.get('page', 1, type=int)
    items_per_page = 10

    # Critérios de filtragem
    search_order_id = request.args.get('searchOrderId', type=str)
    search_equipment = request.args.get('searchEquipment', type=str)
    search_client = request.args.get('searchClient', type=str)
    filter_status = request.args.get('filterStatus', type=str)
    filter_priority = request.args.get('filterPriority', type=str)
    filter_start_date = request.args.get('filterStartDate', type=str)
    filter_end_date = request.args.get('filterEndDate', type=str)

    # Query para obter todas as orders com filtros aplicados
    query = Order.query
    categorias = Categoria.query.all()
    estados = Estado

    if search_order_id:
        query = query.filter(cast(Order.numero_ordem, db.String).ilike(f'%{search_order_id}%'))
    if search_equipment:
        query = query.filter(Order.equipamento.ilike(f'%{search_equipment}%'))
    if search_client:
        query = query.filter(Order.cliente.ilike(f'%{search_client}%'))
    if filter_status:
        query = query.filter(Order.status == filter_status)
    if filter_priority:
        query = query.filter(Order.prioridade == filter_priority)
    if filter_start_date:
        query = query.filter(Order.data_inicio >= filter_start_date)
    if filter_end_date:
        query = query.filter(Order.previsao_entrega <= filter_end_date)

    # Paginar as orders
    orders_paginated = query.paginate(page=page, per_page=items_per_page, error_out=False)
    
    # Obter a data e hora atual
    current_time = datetime.now()

    total_ordens = len(orders_paginated.items)
    total_pages = orders_paginated.pages
    
    valor_total = request.args.get('valor_total', default=0, type=float)

    # Passar os dados filtrados para o template
    response = make_response(render_template('/ordens/ordens.html',
                                        email=current_user.email,
                                        orders_items=orders_paginated.items,  # Corrigido para orders_paginated
                                        total_ordens=total_ordens,
                                        total_pages=total_pages,
                                        current_page=page,
                                        filter_start_date=filter_start_date,
                                        filter_end_date=filter_end_date,
                                        categorias=categorias,
                                        valor_total=valor_total))
    
    # Atualize o cookie 'last_page_load_time' com o horário atual
    response.set_cookie('last_page_load_time', current_time.isoformat())
    return response


@dashboard_bp.route('/ordem_edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
def ordem_edit(order_id):
    # Busca a ordem pelo ID
    ordem = Order.query.get_or_404(order_id)
    
    # Consultar todos os clientes
    clientes = Client.query.all()
    categorias = Categoria.query.all()
    opcoes_pagamento = ["Transferência bancária", "Link de pagamento", "Cartão de crédito", 
                            "Cartão de débito", "Pix", "Boleto bancário", "Dinheiro em espécie"]

    if request.method == 'POST':
        current_app.logger.info("Dados recebidos do formulário: %s", request.form)
        # Obtenha os dados do formulário de edição
        ordem.operador = request.form['operador']
        ordem.data_inicio = request.form['data_inicio']
        ordem.previsao_entrega = request.form['prev_entrega']
        ordem.cliente = request.form['cliente']
        ordem.equipamento = request.form['equipamento']
        ordem.categoria = request.form['categoria']
        ordem.prioridade = request.form['prioridade']
        ordem.status = request.form['status']

        # Atualiza os itens
        items_json = request.form.get('items')
        if items_json:
            ordem.items = json.loads(items_json)

        # Calcular o total da ordem
        total_ordem = sum(item['valorTotal'] for item in ordem.items)

        ordem.observacoes = request.form['observacoes']

        # Faça commit para efetivar as alterações no banco de dados
        db.session.commit()

        # Redirecione para a página de detalhes da ordem ou para onde desejar após editar a ordem
        return redirect(url_for('dashboard.ordens'))

    # Renderize o template do formulário de edição e passe a ordem como contexto
    return render_template('/ordens/ordem_edit.html', email=current_user.email, ordem=ordem, clientes=clientes, opcoes_pagamento=opcoes_pagamento,
                        categorias=categorias, items=json.dumps(ordem.items), valor_total=ordem.valor_total)

@dashboard_bp.route('/ordem_delete/<int:order_id>', methods=['POST'])
@login_required
def ordem_delete(order_id):
    # Busca a ordem pelo ID
    ordem = Order.query.get_or_404(order_id)

    # Delete a ordem do banco de dados
    db.session.delete(ordem)
    db.session.commit()

    # Redireciona para a página de lista de ordens após a deleção
    return redirect(url_for('dashboard.ordens'))


@dashboard_bp.route('/ordem_status/<int:order_id>', methods=['POST'])
@login_required
def ordem_status(order_id):
    # Buscar a ordem pelo ID
    ordem = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        # Obter o novo status da ordem do formulário
        novo_status = request.form['novo_status']

        # Atualizar o status da ordem
        ordem.status = novo_status

        # Efetivar a alteração no banco de dados
        db.session.commit()

        # Redirecionar para a página de ordens após a atualização do status
        return redirect(url_for('dashboard.ordens'))

    # Redirecionar para a página de detalhes da ordem se o método não for POST
    return redirect(url_for('dashboard.ordem_edit', order_id=order_id))


@dashboard_bp.route('/gerar_pdf/<int:order_id>')
@login_required
def gerar_pdf(order_id):
    # Busque a ordem pelo ID
    ordem = Order.query.get_or_404(order_id)

    # Renderize o template para o PDF
    rendered_html = render_template('/base/pdf_template.html', ordem=ordem)

    # Gere o PDF
    pdf = pdfkit.from_string(rendered_html, False)

    # Retorne o PDF como uma resposta
    response = Response(pdf, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=ordem_servico_{}.pdf'.format(order_id)

    return response

@dashboard_bp.route('/criar_cliente', methods=['GET', 'POST'])
@login_required
def criar_cliente():
    if request.method == 'POST':
        # Obtenha os dados do formulário
        nome = request.form['nome']
        email = request.form['email']
        logradouro = request.form.get('logradouro', None)
        cep = request.form.get('cep', None)
        numero = request.form.get('numero', None)
        bairro = request.form.get('bairro', None)
        cpf_cnpj = request.form['cpf_cnpj']
        telefone = request.form.get('telefone', None)
        uf = request.form.get('uf')

        # Verifique se o CPF ou CNPJ já existe no banco de dados
        cliente_existente = Client.query.filter_by(cpf_cnpj=cpf_cnpj).first()
        if cliente_existente:
            return jsonify({'error': 'CPF ou CNPJ já existente'}), 400
        
        # Verifique se o email já existe
        email_existente = Client.query.filter_by(email=email).first()
        if email_existente:
            return jsonify({'error': 'O e-mail já está em uso. Por favor, escolha outro.'}), 400
        
        # Crie um novo cliente com os dados do formulário
        novo_cliente = Client(
            nome=nome,
            email=email,
            logradouro=logradouro,
            cep=cep,
            numero=numero,
            bairro=bairro,
            cpf_cnpj=cpf_cnpj,
            telefone=telefone,
            uf=uf
        )

        # Adicione o novo cliente ao banco de dados
        db.session.add(novo_cliente)
        db.session.commit()
        
        # Retorne o URL para onde você deseja redirecionar após adicionar o cliente com sucesso
        return jsonify({'redirect': url_for('dashboard.clientes')})
            
    # Se o método for GET, renderize o template para criar um novo cliente
    return render_template('clientes/client_form.html')

@dashboard_bp.route('/client')
@login_required
def clientes():
    # Configurações de paginação
    page = request.args.get('page', 1, type=int)
    items_per_page = 10  # Número de itens por página

    # Critérios de filtragem e pesquisa
    search_nome = request.args.get('searchNome', type=str)
    search_email = request.args.get('searchEmail', type=str)
    search_cpf_cnpj = request.args.get('searchCpfCnpj', type=str)
    search_telefone = request.args.get('searchTelefone', type=str)
    search_uf = request.args.get('searchUF', type=str)

    # Query para obter todos os clientes com filtros aplicados
    query = Client.query

    if search_nome:
        query = query.filter(Client.nome.ilike(f'%{search_nome}%'))
    if search_email:
        query = query.filter(Client.email.ilike(f'%{search_email}%'))
    if search_cpf_cnpj:
        query = query.filter(Client.cpf_cnpj.ilike(f'%{search_cpf_cnpj}%'))
    if search_telefone:
        query = query.filter(Client.telefone.ilike(f'%{search_telefone}%'))
    if search_uf:
        query = query.filter(Client.uf.ilike(f'%{search_uf}%'))

    # Paginar os clientes
    clientes_paginados = query.paginate(page=page, per_page=items_per_page, error_out=False)
    
    # Calcular o número total de páginas
    total_pages = clientes_paginados.pages

    # Renderizar o template e passar os clientes paginados, página atual, e número total de páginas como contexto
    return render_template('/clientes/client.html', email=current_user.email, clientes=clientes_paginados, current_page=page, total_pages=total_pages)


@dashboard_bp.route('/editar_cliente/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    cliente = Client.query.get_or_404(cliente_id)
    
    # Defina o dicionário de estados
    estados = {
        'AC': 'Acre',
        'AL': 'Alagoas',
        'AP': 'Amapá',
        'AM': 'Amazonas',
        'BA': 'Bahia',
        'CE': 'Ceará',
        'DF': 'Distrito Federal',
        'ES': 'Espírito Santo',
        'GO': 'Goiás',
        'MA': 'Maranhão',
        'MT': 'Mato Grosso',
        'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais',
        'PA': 'Pará',
        'PB': 'Paraíba',
        'PR': 'Paraná',
        'PE': 'Pernambuco',
        'PI': 'Piauí',
        'RJ': 'Rio de Janeiro',
        'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul',
        'RO': 'Rondônia',
        'RR': 'Roraima',
        'SC': 'Santa Catarina',
        'SP': 'São Paulo',
        'SE': 'Sergipe',
        'TO': 'Tocantins',
    }
    
    if request.method == 'POST':
        # Obter os dados do formulário
        cliente.nome = request.form['nome']
        cliente.email = request.form['email']
        cliente.logradouro = request.form.get('logradouro', None)
        cliente.cep = request.form.get('cep', None)
        cliente.numero = request.form.get('numero', None)
        cliente.bairro = request.form.get('bairro', None)
        cliente.cpf_cnpj = request.form['cpf_cnpj']
        cliente.telefone = request.form.get('telefone', None)
        cliente.uf = request.form.get('uf')
        
        # Atualizar o cliente no banco de dados
        db.session.commit()
        
        # Redirecionar para a página de clientes após a edição
        return redirect(url_for('dashboard.clientes'))
    
    # Renderizar o formulário de edição com os dados do cliente
    return render_template('/clientes/client_edit.html', cliente=cliente, estados=estados)


@dashboard_bp.route('/excluir_cliente/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def excluir_cliente(cliente_id):
    cliente = Client.query.get_or_404(cliente_id)
    
    if request.method == 'POST':
        # Excluir o cliente do banco de dados
        db.session.delete(cliente)
        db.session.commit()
        
        # Redirecionar para a página de clientes após a exclusão
        return redirect(url_for('dashboard.clientes'))
    
    # Renderizar o modal de confirmação de exclusão
    return render_template('/clientes/modal_excluir_cliente.html', cliente=cliente)

############# produtos e serviços
@dashboard_bp.route('/criar_item', methods=['GET', 'POST'])
@login_required
def criar_item():
    if request.method == 'POST':
        descricao = request.form['descricao']
        codigo = request.form['codigo']
        preco_str = request.form['preco']
        categoria_item = request.form['categoria_item']
        
        # Validação de entrada
        if not descricao or not codigo or not preco_str or not categoria_item:
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('dashboard.criar_item'))
        
        try:
            preco = float(preco_str.replace('R$', '').replace('.', '').replace(',', '.'))
        except ValueError:
            flash('Preço inválido.', 'error')
            return redirect(url_for('dashboard.criar_item'))

        novo_item = Item(
            descricao=descricao,
            codigo=codigo,
            preco=preco,
            categoria_item=categoria_item
        )

        try:
            # Adiciona o novo item ao banco de dados
            db.session.add(novo_item)
            db.session.commit()
            flash('Item criado com sucesso!', 'success')
            return redirect(url_for('dashboard.listar_itens'))
        except Exception as e:
            flash('Erro ao criar o item.', 'error')
            # Você pode querer fazer log do erro para investigação futura
            print(e)
            return redirect(url_for('dashboard.criar_item'))

    return render_template('items/item_form.html')

@dashboard_bp.route('/itens')
@login_required
def listar_itens():
    # Configurações de paginação
    page = request.args.get('page', 1, type=int)
    items_per_page = 10  # Número de itens por página

    # Critérios de filtragem
    search_descricao = request.args.get('searchDescricao', type=str)
    search_codigo = request.args.get('searchCodigo', type=str)
    filter_categoria_item = request.args.get('filterCategoriaItem', type=str)

    # Query para obter todos os itens com filtros aplicados
    query = Item.query

    if search_descricao:
        query = query.filter(Item.descricao.ilike(f'%{search_descricao}%'))
    if search_codigo:
        query = query.filter(Item.codigo.ilike(f'%{search_codigo}%'))
    if filter_categoria_item:
        query = query.filter(Item.categoria_item == filter_categoria_item)

    # Paginar os itens
    itens_paginados = query.paginate(page=page, per_page=items_per_page, error_out=False)

    # Calcular o número total de páginas
    total_pages = itens_paginados.pages

    # Renderize o template para exibir os itens paginados, passando a lista de itens, a página atual e o número total de páginas como contexto
    return render_template('/items/items.html', itens=itens_paginados.items, current_page=page, total_pages=total_pages)


@dashboard_bp.route('/editar_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def editar_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Defina o dicionário de categorias
    categorias = {
        'produtos': 'Produtos',
        'servicos': 'Serviços',
        # Adicione mais categorias conforme necessário
    }
    
    if request.method == 'POST':
        # Obter os dados do formulário de edição
        item.descricao = request.form['descricao']
        item.codigo = request.form['codigo']
        
        # Obter o preço do formulário e remover todos os caracteres não numéricos, exceto pontos e vírgulas
        preco_str = re.sub(r'[^\d\.,]', '', request.form['preco'])

        # Substituir vírgulas por pontos (para garantir que o Python entenda como um número float)
        preco_str = preco_str.replace(',', '.')

        # Converter a string de preço para float
        item.preco = float(preco_str)
        
        item.categoria = request.form['categoria'] # Aqui é onde você deve acessar 'categoria_item'


        # Faça commit para efetivar as alterações no banco de dados
        db.session.commit()

        # Redirecione para a página de lista de itens após a edição
        return redirect(url_for('dashboard.listar_itens'))

    # Renderize o template do formulário de edição com os dados do item
    return render_template('/items/item_edit.html', item=item, categorias=categorias)


@dashboard_bp.route('/excluir_item/<int:item_id>', methods=['POST'])
@login_required
def excluir_item(item_id):
    # Busca o item pelo ID
    item = Item.query.get_or_404(item_id)

    # Delete o item do banco de dados
    db.session.delete(item)
    db.session.commit()

    # Redireciona para a página de lista de itens após a exclusão
    return redirect(url_for('dashboard.listar_itens'))


@dashboard_bp.route('/buscar_itens')
@login_required
def buscar_itens():
    search_term = request.args.get('search_term', '')

    # Realize a busca no banco de dados com base no termo de pesquisa
    results = Item.query.filter(Item.descricao.ilike(f'%{search_term}%')).all()

    # Transforme os resultados em um formato adequado para resposta Ajax
    response = [{'descricao': item.descricao, 'codigo': item.codigo, 'preco': item.preco, 'categoria_item': item.categoria_item} for item in results]

    return jsonify(response)

###### Categorias 
@dashboard_bp.route('/criar_categoria', methods=['GET', 'POST'])
@login_required
def criar_categoria():
    if request.method == 'POST':
        nome_categoria = request.form['nome_categoria']
        
        # Validação de entrada
        if not nome_categoria:
            flash('O nome da categoria é obrigatório.', 'error')
            return redirect(url_for('dashboard.criar_categoria'))
        
        # Verifica se a categoria já existe no banco de dados
        categoria_existente = Categoria.query.filter_by(nome=nome_categoria).first()
        if categoria_existente:
            flash('Essa categoria já existe.', 'error')
            return redirect(url_for('dashboard.criar_categoria'))
        
        nova_categoria = Categoria(nome=nome_categoria)

        try:
            # Adiciona a nova categoria ao banco de dados
            db.session.add(nova_categoria)
            db.session.commit()
            flash('Categoria criada com sucesso!', 'success')
            return redirect(url_for('dashboard.listar_categorias'))
        except Exception as e:
            flash('Erro ao criar a categoria.', 'error')
            print(e)
            return redirect(url_for('dashboard.criar_categoria'))

    return render_template('category/category_form.html',)


@dashboard_bp.route('/categorias')
@login_required
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('category/category.html', categorias=categorias)


@dashboard_bp.route('/excluir_categoria/<int:categoria_id>', methods=['POST'])
@login_required
def excluir_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('dashboard.listar_categorias'))
