from app.models.models import Order  # Importe o modelo Order
from flask import Blueprint, render_template,request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from app import db
from decimal import Decimal
import math

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
        # Ajuste da sequência antes de inserir a nova ordem
        max_numero_ordem = db.session.query(Order.numero_ordem).order_by(Order.numero_ordem.desc()).first()
        if max_numero_ordem is None:
            next_value = 1
        else:
            next_value = max_numero_ordem[0] + 1
        with db.engine.connect() as connection:
            connection.execute(text(f"ALTER SEQUENCE orders_numero_ordem_seq RESTART WITH {next_value};"))

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

        # Crie uma nova ordem sem definir explicitamente o valor de numero_ordem
        nova_ordem = Order(operador=operador, data_inicio=data_inicio, previsao_entrega=previsao_entrega,
                    cliente=cliente, equipamento=equipamento, categoria=categoria,
                    prioridade=prioridade, status=status, valor_inicial=valor_inicial,
                    observacoes=observacoes)

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
    items_per_page = request.args.get('items_per_page', 10, type=int)
    
    # Calcular o índice inicial para a paginação
    start_index = (page - 1) * items_per_page
    
    # Obter as ordens para a página atual
    orders = Order.query.order_by(Order.id).offset(start_index).limit(items_per_page).all()
    
    # Total de ordens
    total_ordens = Order.query.count()
    
    # Calcular o número total de páginas
    total_pages = math.ceil(total_ordens / items_per_page)
    
    # Contagem de ordens concluídas e canceladas
    ordens_concluidas = Order.query.filter_by(status='Concluida').count()
    ordens_canceladas = Order.query.filter_by(status='Cancelada').count()
    
    # Lógica para exibir o dashboard
    return render_template('/ordens/ordens.html', 
                        email=current_user.email, 
                        orders=orders, 
                        total_ordens=total_ordens,
                        total_pages=total_pages,
                        current_page=page,
                        ordens_concluidas=ordens_concluidas, 
                        ordens_canceladas=ordens_canceladas)

