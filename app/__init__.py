# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models.models import db
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@db/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register the blueprints
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Criar o banco de dados se ele não existir
    with app.app_context():
        db.create_all()

    return app