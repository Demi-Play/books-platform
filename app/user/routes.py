from functools import wraps
from flask import Blueprint, flash, redirect, render_template, jsonify, request, url_for, current_app
from flask_login import login_required, current_user
from app.auth.models import User, UserRole
from app.books.models import Book, Bookmark, db, Like, Comment, Genre
import os

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

@user_bp.route('/bookmark/<int:bookmark_id>/delete', methods=['POST'])
@login_required
def delete_bookmark(bookmark_id):
    """Удаление закладки"""
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    
    # Проверка, принадлежит ли закладка текущему пользователю
    if bookmark.user_id != current_user.id:
        flash('Недостаточно прав для удаления закладки', 'error')
        return redirect(url_for('user.dashboard'))
    
    db.session.delete(bookmark)
    db.session.commit()
    
    flash('Закладка успешно удалена', 'success')
    return redirect(url_for('user.dashboard'))

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
        roles=list(UserRole),
        UserRole=UserRole
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

@admin_bp.route('/users/unblock/<int:user_id>', methods=['GET', 'POST'])
@roles_required(UserRole.ADMIN)
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Разблокировка
    if user.blocked_until:
        user.unblock()
        flash(f'Пользователь {user.username} разблокирован', 'success')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/books')
@roles_required(UserRole.ADMIN)
def manage_books():
    """Управление книгами в админке"""
    books = Book.query.all()
    return render_template(
        'admin/books.html',
        books=books,
        UserRole=UserRole
    )

@admin_bp.route('/books/<int:book_id>/update', methods=['POST'])
@roles_required(UserRole.ADMIN)
def update_book(book_id):
    """Обновление статуса книги"""
    book = Book.query.get_or_404(book_id)
    
    # Обновление статуса
    new_status = request.form.get('status')
    if new_status in ['pending', 'approved', 'rejected']:
        book.status = new_status
        db.session.commit()
        flash(f'Статус книги "{book.title}" обновлен', 'success')
    else:
        flash('Некорректный статус', 'error')
    
    return redirect(url_for('admin.manage_books'))

@admin_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@roles_required(UserRole.ADMIN)
def delete_book(book_id):
    """Удаление книги"""
    book = Book.query.get_or_404(book_id)
    
    # Удаление связанных данных
    Bookmark.query.filter_by(book_id=book_id).delete()
    Like.query.filter_by(book_id=book_id).delete()
    Comment.query.filter_by(book_id=book_id).delete()
    
    # Удаление файла книги
    if book.file_path:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], book.file_path))
        except:
            pass
    
    # Удаление книги
    db.session.delete(book)
    db.session.commit()
    
    flash(f'Книга "{book.title}" успешно удалена', 'success')
    return redirect(url_for('admin.manage_books'))

@admin_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@roles_required(UserRole.ADMIN)
def edit_book(book_id):
    """Редактирование книги"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        # Обновление данных книги
        book.title = request.form.get('title')
        book.description = request.form.get('description')
        book.status = request.form.get('status')
        
        # Обновление жанров
        book.genres.clear()
        genre_ids = request.form.getlist('genres')
        for genre_id in genre_ids:
            genre = Genre.query.get(genre_id)
            if genre:
                book.genres.append(genre)
        
        db.session.commit()
        flash('Книга успешно обновлена', 'success')
        return redirect(url_for('admin.manage_books'))
    
    # Получение списка жанров для формы
    genres = Genre.query.all()
    return render_template(
        'admin/book_edit.html',
        book=book,
        genres=genres,
        UserRole=UserRole
    )

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
        book_stats=book_stats,
        UserRole=UserRole
    )

    
@moderator_bp.route('/publications')
@roles_required(UserRole.MODERATOR)
def manage_publications():
    books = Book.query.all()
    return render_template('moderator/publications.html', books=books, UserRole=UserRole)

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


    
