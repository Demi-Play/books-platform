from flask import Blueprint, render_template
from app.books.models import Book, Genre

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница"""
    # Получаем последние 6 книг
    latest_books = Book.query.order_by(Book.published_at.desc()).limit(6).all()
    
    # Получаем список жанров
    genres = Genre.query.all()
    
    return render_template(
        'index.html', 
        latest_books=latest_books, 
        genres=genres
    )
