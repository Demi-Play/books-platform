from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.books.models import Book, Bookmark

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """Личный кабинет пользователя"""
    # Получаем закладки пользователя
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    
    # Получаем загруженные книги
    uploaded_books = Book.query.filter_by(author_id=current_user.id).all()
    
    return render_template(
        'user/dashboard.html', 
        bookmarks=bookmarks, 
        uploaded_books=uploaded_books
    )

@user_bp.route('/bookmarks')
@login_required
def bookmarks():
    """Список закладок пользователя"""
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'user/bookmarks.html', 
        bookmarks=bookmarks
    )
