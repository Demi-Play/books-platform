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
    
@admin_bp.route('/users', methods=['GET'])
@roles_required(UserRole.ADMIN)
def manage_users():
    users = User.query.all()
    return render_template(
        'admin/users.html', 
        users=users, 
        roles=list(UserRole)
    )

@admin_bp.route('/users/update', methods=['POST'])
@roles_required(UserRole.ADMIN)
def update_users():
    for user in User.query.all():
        # Обновление роли
        role_key = f'role_{user.id}'
        active_key = f'active_{user.id}'
        
        if role_key in request.form:
            try:
                user.role = UserRole(request.form[role_key])
            except ValueError:
                flash(f'Некорректная роль для пользователя {user.username}', 'error')
        
        # Обновление статуса активности
        user.is_active_status = active_key in request.form
    
    try:
        db.session.commit()
        flash('Информация о пользователях обновлена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка обновления: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/block', methods=['POST'])  # Изменен маршрут
@roles_required(UserRole.ADMIN)
def block_user():
    user_id = request.form.get('user_id')
    duration = request.form.get('duration', type=int, default=24)
    reason = request.form.get('reason')
    
    user = User.query.get_or_404(user_id)
    
    # Блокировка или разблокировка
    if user.blocked_until:
        user.unblock()
        flash(f'Пользователь {user.username} разблокирован', 'success')
    else:
        user.block(duration=duration, reason=reason)
        flash(
            f'Пользователь {user.username} заблокирован на {duration} часов. '
            f'Причина: {reason}', 
            'warning'
        )
    
    return redirect(url_for('admin.manage_users'))



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


    
