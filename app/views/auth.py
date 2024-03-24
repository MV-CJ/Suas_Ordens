from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user
from app import db
from flask import jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.models.models import Users  # Importe apenas dentro da função para evitar importação circular

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Users.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)  # Autentica o usuário
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('auth.login'))

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
