from flask import Blueprint, render_template
from app.auth.models import User
from app.books.models import Book, Genre, ReadingClub
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница"""
    # Получаем последние 6 книг
    latest_books = Book.query.order_by(Book.published_at.desc()).limit(6).all()
    
    # Получаем список жанров
    genres = Genre.query.all()
    trending_books = Book.query.filter_by(status='approved').outerjoin(Book.likes).group_by(Book).order_by(func.count(Book.likes).desc()).limit(6).all()
    
    total_books = Book.query.count()
    total_users = User.query.count()
    total_clubs = ReadingClub.query.count()
    
    return render_template(
        'index.html', 
        trending_books=trending_books,
        total_books=total_books,
        total_users=total_users,
        total_clubs=total_clubs,
        latest_books=latest_books, 
        genres=genres
    )
    
