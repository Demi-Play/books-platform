from datetime import datetime
import os
from flask import Blueprint, flash, redirect, request, jsonify, render_template, current_app, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserRole, db
from .forms import PasswordChangeForm, RegistrationForm, LoginForm, ProfileUpdateForm
from werkzeug.utils import secure_filename


auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    
    if request.method == 'POST':
        if form.validate():
            # Проверка существования пользователя
            existing_user = User.query.filter(
                (User.username == form.username.data) | 
                (User.email == form.email.data)
            ).first()
            
            if existing_user:
                flash('Пользователь с таким именем или email уже существует', 'error')
                return redirect(url_for('auth.register'))
            
            # Создание нового пользователя
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                role=UserRole.USER
            )
            new_user.set_password(form.password.data)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('auth.login'))
        
        # Обработка ошибок валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
        
        return render_template('auth/register.html', form=form)
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                user.last_login = datetime.now()
                db.session.commit()
                
                flash('Вход выполнен успешно!', 'success')
                return redirect(url_for('user.dashboard'))
            
            flash('Неверный email или пароль', 'error')
            return redirect(url_for('auth.login'))
        
        # Обработка ошибок валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
        
        return render_template('auth/login.html', form=form)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm(request.form)
    
    if request.method == 'POST':
        if form.validate():
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.bio = form.bio.data
            
            # if form.avatar.data:
            #     # Логика загрузки аватара
            #     avatar_file = request.files['avatar']
            #     filename = secure_filename(avatar_file.filename)
            #     avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', filename)
            #     avatar_file.save(avatar_path)
            #     current_user.avatar = avatar_path
            
            db.session.commit()
            
            flash('Профиль успешно обновлен', 'success')
            return redirect(url_for('auth.profile'))
        
        # Обработка ошибок валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
        
        return render_template('auth/profile.html', form=form)
    
    return render_template('auth/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm(request.form)
    
    if request.method == 'POST':
        if form.validate():
            if not current_user.check_password(form.old_password.data):
                flash('Неверный текущий пароль', 'error')
                return redirect(url_for('auth.change_password'))
            
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('user.dashboard'))
        
        # Обработка ошибок валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
        
        return render_template('auth/change_password.html', form=form)
    
    return render_template('auth/change_password.html', form=form)
