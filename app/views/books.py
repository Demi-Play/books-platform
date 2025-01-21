from flask import Blueprint, request, redirect, url_for, render_template
from app import db
from app.models.book import Book
from app.models.log import LogEntry

bp = Blueprint('books', __name__)

@bp.route('/books', methods=['GET'])
def book_list():
    books = Book.query.all()
    return render_template('books/book_list.html', books=books)

@bp.route('/books/new', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        content = request.files['content'].read()  # Чтение содержимого книги

        new_book = Book(title=title, author=author, description=description, content=content)
        db.session.add(new_book)
        db.session.commit()

        # Логирование действия
        log_entry = LogEntry(action='Created', book_id=new_book.id)
        db.session.add(log_entry)
        db.session.commit()

        return redirect(url_for('books.book_list'))
    
    return render_template('books/create_book.html')

@bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.description = request.form['description']
        
        if 'content' in request.files:
            book.content = request.files['content'].read()

        db.session.commit()

        # Логирование действия
        log_entry = LogEntry(action='Edited', book_id=book.id)
        db.session.add(log_entry)
        db.session.commit()

        return redirect(url_for('books.book_list'))

    return render_template('books/edit_book.html', book=book)

@bp.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Логирование действия перед удалением
    log_entry = LogEntry(action='Deleted', book_id=book.id)
    
    db.session.delete(book)
    db.session.add(log_entry)
    db.session.commit()

    return redirect(url_for('books.book_list'))
