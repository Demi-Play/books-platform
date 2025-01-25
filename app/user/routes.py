from functools import wraps
from flask import Blueprint, flash, redirect, render_template, jsonify, request, url_for
from flask_login import login_required, current_user
from app.auth.models import User, UserRole
from app.books.models import Book, Bookmark, db

user_bp = Blueprint('user', __name__)
admin_bp = Blueprint('admin', __name__)
moderator_bp = Blueprint('moderator', __name__)
author_bp = Blueprint('author', __name__)

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
        uploaded_books=uploaded_books,
        UserRole=UserRole
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
    
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('Недостаточно прав', 'error')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
    
@admin_bp.route('/users')
@roles_required(UserRole.ADMIN)
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@author_bp.route('/dashboard/author')
@login_required
def author_dashboard():
    books = Book.query.filter_by(author_id=current_user.id).all()
    
    book_stats = {
        'total_books': len(books),
        'published_books': len([b for b in books if b.status == 'approved']),
        'pending_books': len([b for b in books if b.status == 'pending']),
        'draft_books': len([b for b in books if b.status == 'rejected']),
        'total_likes': sum(len(book.likes) for book in books)
    }
    
    return render_template(
        'author/dashboard.html', 
        books=books, 
        book_stats=book_stats
    )

@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@roles_required(UserRole.ADMIN)
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.role = request.form.get('role')
    user.is_active = request.form.get('is_active', type=bool)
    db.session.commit()
    
@moderator_bp.route('/publications')
@roles_required(UserRole.MODERATOR)
def manage_publications():
    books = Book.query.all()
    return render_template('moderator/publications.html', books=books)

@moderator_bp.route('/book/<int:book_id>/approve', methods=['POST'])
@roles_required(UserRole.MODERATOR)
def approve_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.status = 'approved'
    db.session.commit()
    books = Book.query.all()
    return redirect(url_for('moderator.manage_publications', books=books))

@moderator_bp.route('/book/<int:book_id>/reject', methods=['POST'])
@roles_required(UserRole.MODERATOR)
def reject_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.status = 'rejected'
    db.session.commit()
    books = Book.query.all()
    return redirect(url_for('moderator.manage_publications', books=books))


    
