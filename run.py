import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect


# Импорт моделей
from app.auth.models import db, User
from app.books.models import Book, Genre, ReadingClub

# Импорт блюпринтов
from app.auth.routes import auth_bp
from app.books.routes import books_bp
from app.main.routes import main_bp
from app.user.routes import user_bp
from app.user.routes import admin_bp
from app.user.routes import moderator_bp
from app.user.routes import author_bp
from app.reading_clubs.routes import reading_clubs_bp

class Config:
    """Конфигурация приложения"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'tamarasecretagafonovakey')
    
    # Конфигурация базы данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///booksplatform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки безопасности
    SESSION_COOKIE_SECURE = False  # Изменено на False для локальной разработки
    REMEMBER_COOKIE_SECURE = False  # Изменено на False для локальной разработки
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Настройки CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', 'csrf-secret-key')
    WTF_CSRF_TIME_LIMIT = 3600  # 1 час
    
    # Настройки загрузки файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 МБ
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'uploads')

def create_app(config_class=Config):
    """Фабрика приложений"""
    app = Flask(__name__, template_folder='./app/templates')
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
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
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(author_bp, url_prefix='/author')
    app.register_blueprint(moderator_bp, url_prefix='/moderator')
    app.register_blueprint(reading_clubs_bp, url_prefix='/clubs')
    
    
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
    
    from flask import send_from_directory

    # Добавить маршрут для обслуживания файлов из uploads
    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(
            os.path.join(current_app.root_path, 'uploads'), 
            filename
        )
    
    # Запуск приложения
    app.run(
        # debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
        debug=False
    )

if __name__ == '__main__':
    run_app()
