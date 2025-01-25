from datetime import datetime, timedelta
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    
    
    # Персональные данные
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(255))

    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    # Связи
    books = db.relationship('Book', backref='author', lazy='dynamic')
    reading_clubs = db.relationship('ReadingClub', secondary='club_members', back_populates='members')
    recommendations = db.relationship('BookRecommendation', backref='user')

    is_active_status = db.Column(db.Boolean, default=True)
    blocked_until = db.Column(db.DateTime, nullable=True)
    block_reason = db.Column(db.String(255), nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime, nullable=True)

    @property
    def is_active(self):
        """
        Проверка активности пользователя с учетом:
        1. Статуса активности
        2. Временной блокировки
        3. Количества неудачных попыток входа
        """
        # Если пользователь явно деактивирован
        if not self.is_active_status:
            return False
        
        # Проверка временной блокировки
        if self.blocked_until and self.blocked_until > datetime.now():
            return False
        
        # Сброс блокировки, если время истекло
        if self.blocked_until and self.blocked_until <= datetime.now():
            self.blocked_until = None
            self.failed_login_attempts = 0
        
        return True

    def block(self, duration=None, reason=None):
        """
        Блокировка пользователя
        
        :param duration: Длительность блокировки в часах
        :param reason: Причина блокировки
        """
        self.is_active_status = False
        
        if duration:
            self.blocked_until = datetime.now() + timedelta(hours=duration)
        
        self.block_reason = reason
        db.session.commit()

    def unblock(self):
        """Разблокировка пользователя"""
        self.is_active_status = True
        self.blocked_until = None
        self.failed_login_attempts = 0
        self.block_reason = None
        db.session.commit()

    def increment_failed_login(self):
        """
        Увеличение счетчика неудачных попыток входа
        Автоматическая блокировка при превышении лимита
        """
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
        
        # Блокировка после 5 неудачных попыток
        if self.failed_login_attempts >= 5:
            self.block(
                duration=1,  # Блокировка на 1 час
                reason="Превышено количество попыток входа"
            )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
