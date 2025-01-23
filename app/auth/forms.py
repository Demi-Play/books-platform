from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

class RegistrationForm(FlaskForm):
    """Форма регистрации пользователя"""
    username = StringField('Имя пользователя', [
        DataRequired(message='Обязательное поле'),
        Length(min=3, max=50, message='От 3 до 50 символов')
    ])
    email = StringField('Email', [
        DataRequired(message='Обязательное поле'),
        Email(message='Некорректный email')
    ])
    password = PasswordField('Пароль', [
        DataRequired(message='Обязательное поле'),
        Length(min=8, message='Минимум 8 символов'),
        EqualTo('confirm_password', message='Пароли не совпадают')
    ])
    confirm_password = PasswordField('Подтверждение пароля')

class LoginForm(FlaskForm):
    """Форма входа"""
    email = StringField('Email', [
        DataRequired(message='Обязательное поле'),
        Email(message='Некорректный email')
    ])
    password = PasswordField('Пароль', [
        DataRequired(message='Обязательное поле')
    ])
    remember = BooleanField('Запомнить меня')

class ProfileUpdateForm(FlaskForm):
    """Форма обновления профиля"""
    first_name = StringField('Имя', [
        Optional(),
        Length(max=50, message='Максимум 50 символов')
    ])
    last_name = StringField('Фамилия', [
        Optional(),
        Length(max=50, message='Максимум 50 символов')
    ])
    bio = TextAreaField('О себе', [
        Optional(),
        Length(max=500, message='Максимум 500 символов')
    ])
    avatar = FileField('Аватар', [
        Optional()
    ])

class PasswordChangeForm(FlaskForm):
    """Форма смены пароля"""
    old_password = PasswordField('Текущий пароль', [
        DataRequired(message='Обязательное поле')
    ])
    new_password = PasswordField('Новый пароль', [
        DataRequired(message='Обязательное поле'),
        Length(min=8, message='Минимум 8 символов'),
        EqualTo('confirm_new_password', message='Пароли не совпадают')
    ])
    confirm_new_password = PasswordField('Подтверждение нового пароля')