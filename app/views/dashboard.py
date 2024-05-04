from app.models.models import Order  # Importe o modelo Order
from flask import Blueprint, render_template,request, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import text, cast, desc
from app import db
from decimal import Decimal
from datetime import datetime
import math, uuid

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
    # Renderize o template e passe o número de ordem como contexto
    return render_template('/ordens/ordem_form.html', email=current_user.email, order=order,order_count_plus_one=order_count_plus_one)


@dashboard_bp.route('/salvar_ordem', methods=['POST'])
@login_required
def salvar_ordem():
    if request.method == 'POST':
        # Obter a quantidade atual de ordens
        total_ordens = Order.query.count()

        # Obtenha os dados do formulário
        operador = current_user.first_name + ' ' + current_user.last_name
        data_inicio = request.form['data_inicio']
        previsao_entrega = request.form['prev_entrega']
        cliente = request.form['cliente']
        equipamento = request.form['equipamento']
        categoria = request.form['categoria']
        prioridade = request.form['prioridade']
        status = request.form['status']

        # Remova o símbolo de moeda e substitua a vírgula por ponto no campo valor_inicial
        valor_inicial_str = request.form['vl_inicial']
        valor_inicial_str = valor_inicial_str.replace('R$', '').replace('.', '') # Remover os pontos de milhar
        valor_inicial_str = valor_inicial_str.replace(',', '.') # Substituir a vírgula por ponto

        # Converta para float
        valor_inicial = float(valor_inicial_str)

        observacoes = request.form['observacoes']

        # Calcular o próximo número de ordem sequencial
        next_order_number = total_ordens + 1

        # Crie uma nova ordem com o número de ordem sequencial
        nova_ordem = Order(
            numero_ordem=str(next_order_number),
            operador=operador, 
            data_inicio=data_inicio, 
            previsao_entrega=previsao_entrega,
            cliente=cliente, 
            equipamento=equipamento, 
            categoria=categoria,
            prioridade=prioridade, 
            status=status, 
            valor_inicial=valor_inicial,
            observacoes=observacoes
        )

        # Adicione a nova ordem ao session do banco de dados
        db.session.add(nova_ordem)

        # Faça commit para efetivar a transação no banco de dados
        db.session.commit()

        # Redirecione para a página inicial ou para onde desejar após salvar a ordem
        return redirect(url_for('dashboard.ordens'))

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

    # Passar os dados filtrados para o template
    response = make_response(render_template('/ordens/ordens.html',
                                        email=current_user.email,
                                        orders_items=orders_paginated.items,  # Corrigido para orders_paginated
                                        total_ordens=total_ordens,
                                        total_pages=total_pages,
                                        current_page=page,
                                        filter_start_date=filter_start_date,
                                        filter_end_date=filter_end_date))
    
    # Atualize o cookie 'last_page_load_time' com o horário atual
    response.set_cookie('last_page_load_time', current_time.isoformat())
    return response


@dashboard_bp.route('/ordem_edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
def ordem_edit(order_id):
    # Busca a ordem pelo ID
    ordem = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        # Obtenha os dados do formulário de edição
        ordem.operador = request.form['operador']
        ordem.data_inicio = request.form['data_inicio']
        ordem.previsao_entrega = request.form['prev_entrega']
        ordem.cliente = request.form['cliente']
        ordem.equipamento = request.form['equipamento']
        ordem.categoria = request.form['categoria']
        ordem.prioridade = request.form['prioridade']
        ordem.status = request.form['status']

        # Remova o símbolo de moeda e substitua a vírgula por ponto no campo valor_inicial
        valor_inicial_str = request.form['vl_inicial']
        valor_inicial_str = valor_inicial_str.replace('R$', '').replace('.', '')  # Remover os pontos de milhar
        valor_inicial_str = valor_inicial_str.replace(',', '.')  # Substituir a vírgula por ponto

        # Converta para float
        ordem.valor_inicial = float(valor_inicial_str)

        ordem.observacoes = request.form['observacoes']

        # Faça commit para efetivar as alterações no banco de dados
        db.session.commit()

        # Redirecione para a página de detalhes da ordem ou para onde desejar após editar a ordem
        return redirect(url_for('dashboard.ordens'))

    # Renderize o template do formulário de edição e passe a ordem como contexto
    return render_template('/ordens/ordem_edit.html', email=current_user.email, ordem=ordem)

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