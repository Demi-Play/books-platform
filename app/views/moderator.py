from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app import db
from app.models.book import Book
from app.models.log import LogEntry

moderator_bp = Blueprint('moderator', __name__)
bp = moderator_bp

@bp.route('/books', methods=['GET'])
def manage_books():
    books = Book.query.all()
    return render_template('moderator/manage_books.html', books=books)

@bp.route('/books/<int:book_id>/publish', methods=['POST'])
def publish_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if not book.is_published:
        book.is_published = True
        
        log_entry = LogEntry(action_type='publish', book_id=book.id, moderator_id=current_user.id)
        db.session.add(log_entry)

        # Увеличиваем номер версии книги при публикации
        book.version_number += 1
        
        # Сохраняем изменения в базе данных
        db.session.commit()

    return redirect(url_for('moderator.manage_books'))

@bp.route('/books/<int:book_id>/reject', methods=['POST'])
def reject_book(book_id):
    book = Book.query.get_or_404(book_id)

    if book.is_published:
        book.is_published = False
        
        log_entry = LogEntry(action_type='reject', book_id=book.id, moderator_id=current_user.id)
        db.session.add(log_entry)

        # Сохраняем изменения в базе данных
        db.session.commit()

    return redirect(url_for('moderator.manage_books'))

@bp.route('/books/<int:book_id>/update', methods=['POST'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)

    # Здесь можно добавить логику обновления информации о книге (например: title, author и т.д.)
    
    log_entry = LogEntry(action_type='update', book_id=book.id, moderator_id=current_user.id)
    
    # Увеличиваем номер версии книги при обновлении
    book.version_number += 1
    
    # Сохраняем изменения в базе данных
    db.session.commit()

    return redirect(url_for('moderator.manage_books'))
