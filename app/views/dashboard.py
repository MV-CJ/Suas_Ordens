from app.models.models import Order  # Importe o modelo Order
from flask import Blueprint, render_template,request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from decimal import Decimal

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
    return render_template('/dash/dashboard.html', email=current_user.email,total_ordens=total_ordens,ordens_concluidas=ordens_concluidas,ordens_canceladas=ordens_canceladas)

@dashboard_bp.route('/ordem_form')
@login_required
def ordem_form():
    # Obtenha o número total de ordens no banco de dados
    total_ordens = Order.query.count()
    
    # Incrementa o número total de ordens para obter o próximo número de ordem
    numero_ordem = total_ordens + 1

    # Formate o número de ordem com dois dígitos
    numero_ordem_formatado = "{:02d}".format(numero_ordem)

    # Renderize o template e passe o número de ordem como contexto
    return render_template('/ordens/ordem_form.html', email=current_user.email, numero_ordem=numero_ordem_formatado)

@dashboard_bp.route('/salvar_ordem', methods=['POST'])
@login_required
def salvar_ordem():
    if request.method == 'POST':
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
        valor_inicial_str = valor_inicial_str.replace('R$', '').replace('.', '')  # Remover os pontos de milhar
        valor_inicial_str = valor_inicial_str.replace(',', '.')  # Substituir a vírgula por ponto

        # Converta para float
        valor_inicial = float(valor_inicial_str)

        observacoes = request.form['observacoes']

        # Crie uma nova ordem
        nova_ordem = Order(operador=operador, data_inicio=data_inicio, previsao_entrega=previsao_entrega,
                    cliente=cliente, equipamento=equipamento, categoria=categoria,
                    prioridade=prioridade, status=status, valor_inicial=valor_inicial,
                    observacoes=observacoes)

        # Adicione a nova ordem ao session do banco de dados
        db.session.add(nova_ordem)

        # Faça commit para efetivar a transação no banco de dados
        db.session.commit()

        # Redirecione para a página inicial ou para onde desejar após salvar a ordem
        return redirect(url_for('dashboard.dashboard'))