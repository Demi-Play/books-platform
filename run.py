import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Импорт моделей
from app.auth.models import db, User
from app.books.models import Book, Genre, ReadingClub

# Импорт блюпринтов
from app.auth.routes import auth_bp
from app.books.routes import books_bp
from app.user.routes import user_bp

class Config:
    """Конфигурация приложения"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_super_secret_key')
    
    # Конфигурация базы данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/booksplatform')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки безопасности
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Настройки загрузки файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 МБ
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

def create_app(config_class=Config):
    """Фабрика приложений"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Настройка CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Настройка Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Регистрация блюпринтов
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # Создание папки для загрузок
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def init_database(app):
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()
        
        # Создание базовых жанров, если их нет
        if not Genre.query.first():
            default_genres = [
                'Фантастика', 
                'Детектив', 
                'Роман', 
                'Научпоп', 
                'Биография'
            ]
            for genre_name in default_genres:
                genre = Genre(name=genre_name)
                db.session.add(genre)
            db.session.commit()

def run_app():
    """Запуск приложения"""
    app = create_app()
    
    # Инициализация базы данных
    init_database(app)
    
    # Настройка логирования
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запуск приложения
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )

if __name__ == '__main__':
    run_app()
