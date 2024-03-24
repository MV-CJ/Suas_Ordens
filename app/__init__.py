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
