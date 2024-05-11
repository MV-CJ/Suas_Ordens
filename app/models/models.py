from app import db
from uuid import uuid4
from flask_login import UserMixin
from sqlalchemy import Sequence,text
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 
import uuid

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

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    logradouro = db.Column(db.String(100))
    cep = db.Column(db.String(10))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cpf_cnpj = db.Column(db.String(20), nullable=False, unique=True)
    telefone = db.Column(db.String(20))
    uf = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)  # Adicione esta linha

    def __repr__(self):
        return f'<Client {self.nome}>'

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    numero_ordem = db.Column(db.String(36), unique=True, default=str(uuid.uuid4()), nullable=False)
    operador = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date)
    previsao_entrega = db.Column(db.Date)
    cliente = db.Column(db.String(100), nullable=False)
    equipamento = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    prioridade = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    valor_inicial = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)  # Adicione esta linha

    def __repr__(self):
        return f'''
                Order('{self.numero_ordem}', '{self.operador}', '{self.data_inicio}', '{self.previsao_entrega}', 
                '{self.cliente}', '{self.equipamento}', '{self.categoria}', '{self.prioridade}', '{self.status}', 
                '{self.valor_inicial}', '{self.observacoes}')'''
                
                
class Item(db.Model):
    __tablename__ = 'items'  # Nome da tabela no banco de dados

    id = db.Column(db.Integer, primary_key=True)  # Chave primária
    descricao = db.Column(db.String(100), nullable=False)  # Descrição do item
    codigo = db.Column(db.String(20), unique=True, nullable=False)  # Código único do item
    preco = db.Column(db.Float, nullable=False)  # Preço do item
    categoria_item = db.Column(db.String(50), nullable=False)  # Categoria do item

    def __repr__(self):
        return f"Item('{self.descricao}', '{self.codigo}', '{self.preco}', '{self.categoria_item}')"
