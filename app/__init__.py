from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    
    app.secret_key = 'KpY777865'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@db:5432/SO-db'
    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuração do Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Define a rota de login

    # Importe e registre blueprints aqui
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.models import Users # Importado aqui para evitar circular import
        return Users.query.get(int(user_id))

    login_manager.id_attribute = 'get_id'  # Adicionando esta linha

    return app
app = create_app()

# Cadastro de categorias padrão
def cadastrar_categorias_padrao():
    with app.app_context():
        from app.models.models import Categoria  # Import inside the function
        categorias_padrao = [
            'Eletrônicos',
            'Roupas',
            'Alimentos',
            # Outras categorias...
        ]

        for nome_categoria in categorias_padrao:
            categoria_existente = Categoria.query.filter_by(nome=nome_categoria).first()
            if not categoria_existente:
                nova_categoria = Categoria(nome=nome_categoria)
                db.session.add(nova_categoria)
                db.session.commit()
# Chama a função para cadastrar as categorias padrão ao iniciar a aplicação
cadastrar_categorias_padrao()


def cadastrar_estados_padrao():
    with app.app_context():
        from app.models.models import Estado  # Import inside the function
        estados_padrao = [
            {'sigla': 'AC', 'nome': 'Acre'},
            {'sigla': 'AL', 'nome': 'Alagoas'},
            {'sigla': 'AP', 'nome': 'Amapá'},
            {'sigla': 'AM', 'nome': 'Amazonas'},
            {'sigla': 'BA', 'nome': 'Bahia'},
            {'sigla': 'CE', 'nome': 'Ceará'},
            {'sigla': 'DF', 'nome': 'Distrito Federal'},
            {'sigla': 'ES', 'nome': 'Espírito Santo'},
            {'sigla': 'GO', 'nome': 'Goiás'},
            {'sigla': 'MA', 'nome': 'Maranhão'},
            {'sigla': 'MT', 'nome': 'Mato Grosso'},
            {'sigla': 'MS', 'nome': 'Mato Grosso do Sul'},
            {'sigla': 'MG', 'nome': 'Minas Gerais'},
            {'sigla': 'PA', 'nome': 'Pará'},
            {'sigla': 'PB', 'nome': 'Paraíba'},
            {'sigla': 'PR', 'nome': 'Paraná'},
            {'sigla': 'PE', 'nome': 'Pernambuco'},
            {'sigla': 'PI', 'nome': 'Piauí'},
            {'sigla': 'RJ', 'nome': 'Rio de Janeiro'},
            {'sigla': 'RN', 'nome': 'Rio Grande do Norte'},
            {'sigla': 'RS', 'nome': 'Rio Grande do Sul'},
            {'sigla': 'RO', 'nome': 'Rondônia'},
            {'sigla': 'RR', 'nome': 'Roraima'},
            {'sigla': 'SC', 'nome': 'Santa Catarina'},
            {'sigla': 'SP', 'nome': 'São Paulo'},
            {'sigla': 'SE', 'nome': 'Sergipe'},
            {'sigla': 'TO', 'nome': 'Tocantins'},
        ]

        for estado_data in estados_padrao:
            estado_existente = Estado.query.filter_by(sigla=estado_data['sigla']).first()
            if not estado_existente:
                novo_estado = Estado(sigla=estado_data['sigla'], nome=estado_data['nome'])
                db.session.add(novo_estado)
                db.session.commit()
# Chama a função para cadastrar os estados padrão ao iniciar a aplicação
cadastrar_estados_padrao()             

