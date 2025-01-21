from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()



def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Настройки из config.py

    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    from .models.user import User
    @login_manager.user_loader

    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from .models import user, book, like, bookmark  # Импорт моделей для регистрации в SQLAlchemy

        from .views import auth, books, user  # Импорт вьюх для регистрации маршрутов

        app.register_blueprint(auth.bp)
        app.register_blueprint(books.bp)
        app.register_blueprint(user.bp)

        db.create_all()  # Создание всех таблиц в базе данных при первом запуске

    return app