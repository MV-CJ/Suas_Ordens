from app import db
from uuid import uuid4
from flask_login import UserMixin
from sqlalchemy import Sequence
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print("Password hash set successfully:", self.password_hash)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self): 
        return str(self.id)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, Sequence('order_id_seq'), primary_key=True)
    operador = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=True)  # Alterado para aceitar valores vazios
    previsao_entrega = db.Column(db.Date, nullable=True)  # Alterado para aceitar valores vazios
    cliente = db.Column(db.String(100), nullable=False)
    equipamento = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    prioridade = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    valor_inicial = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Order('{self.operador}', '{self.data_inicio}', '{self.previsao_entrega}', '{self.cliente}', '{self.equipamento}', '{self.categoria}', '{self.prioridade}', '{self.status}', '{self.valor_inicial}', '{self.observacoes}')"