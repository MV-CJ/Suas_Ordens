from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from flask_login import login_user
from app import db
from flask import jsonify
import re

auth_bp = Blueprint('auth', __name__)


def is_strong_password(password):
    # Pelo menos 8 caracteres
    if len(password) < 8:
        return False
    # Pelo menos uma letra maiúscula
    if not re.search("[A-Z]", password):
        return False
    # Pelo menos um caractere especial
    if not re.search("[!@#$%^&*()_+{}[\]:;<>,.?/~`]", password):
        return False
    return True


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.models.models import Users

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Users.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            # Retornaremos uma resposta indicando que as credenciais estão incorretas
            return jsonify({"success": False, "error": "Invalid email or password."}), 401

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    from app.models.models import Users  # Importe apenas dentro da função para evitar importação circular

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if first_name and last_name and email and password and password_confirm:
            # Verifica se as senhas coincidem
            if password != password_confirm:
                return jsonify({"success": False, "errors": ["Passwords do not match."]}), 400

            # Verifica se a senha é forte o suficiente
            if not is_strong_password(password):
                return jsonify({"success": False, "errors": ["Password is not strong enough."]}), 400

            
            # Verifica se o e-mail já está em uso
            existing_user = Users.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({"success": False, "errors": ["Email already exists."]}), 400

            # Cria um novo usuário
            new_user = Users(first_name=first_name, last_name=last_name, email=email, password=password)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "errors": ["Please fill in all fields of the form."]}), 400

    return render_template('register.html')
