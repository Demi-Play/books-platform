from datetime import datetime
import os
from flask import Blueprint, flash, redirect, request, jsonify, render_template, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserRole, db
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm
from werkzeug.utils import secure_filename


auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        if form.validate():
            # Проверка существования пользователя
            existing_user = User.query.filter(
                (User.username == form.username.data) | 
                (User.email == form.email.data)
            ).first()
            
            if existing_user:
                return jsonify({
                    'status': 'error', 
                    'message': 'Пользователь уже существует'
                }), 400
            
            # Создание нового пользователя
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                role=UserRole.USER
            )
            new_user.set_password(form.password.data)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Успешный вход!')
            return render_template('/auth/profile.html')
        
        flash(form.errors)
        return jsonify({
            'status': 'error', 
            'errors': form.errors
        }), 400
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    
    """Аутентификация пользователя"""
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                user.last_login = datetime.now()
                db.session.commit()
                
                flash('Успешный вход!')
                return redirect('profile')
            
            return jsonify({
                'status': 'error', 
                'message': 'Неверный email или пароль'
            }), 401
        
        return jsonify({
            'status': 'error', 
            'errors': form.errors
        }), 400
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Выход пользователя"""
    logout_user()
    return jsonify({
        'status': 'success', 
        'message': 'Выход выполнен'
    }), 200

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    form = ProfileUpdateForm(request.form)
    """Управление профилем пользователя"""
    if request.method == 'GET':
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'bio': current_user.bio
        }), 200
    
    elif request.method == 'PUT':
        form = ProfileUpdateForm(request.form)
        if form.validate():
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.bio = form.bio.data
            
            if form.avatar.data:
                # Логика загрузки аватара
                avatar_file = request.files['avatar']
                filename = secure_filename(avatar_file.filename)
                avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', filename)
                avatar_file.save(avatar_path)
                current_user.avatar = avatar_path
            
            db.session.commit()
            
            return jsonify({
                'status': 'success', 
                'message': 'Профиль обновлен'
            }), 200
        
        return jsonify({
            'status': 'error', 
            'errors': form.errors
        }), 400

@auth_bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    """Смена пароля"""
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({
            'status': 'error', 
            'message': 'Необходимо указать старый и новый пароли'
        }), 400
    
    if not current_user.check_password(old_password):
        return jsonify({
            'status': 'error', 
            'message': 'Неверный текущий пароль'
        }), 400
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': 'Пароль успешно изменен'
    }), 200
