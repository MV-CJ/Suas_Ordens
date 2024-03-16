from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    app.secret_key = 'KpY777865'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@db:5432/SO-db'
    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #Importe e registre blueprints aqui
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    
    with app.app_context():
        db.create_all()

    return app
