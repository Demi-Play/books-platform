from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms import LoginForm, RegistrationForm, ProfileForm

auth_bp = Blueprint('auth', __name__)
bp = auth_bp  # Исправлено на правильное определение Blueprint

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('books.book_list'))
        
        flash('Invalid username or password.')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.')
        
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash('Profile updated successfully!')

    return render_template('user/profile.html', form=form)
