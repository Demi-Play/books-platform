from flask import Blueprint, abort, flash, redirect, request, jsonify, render_template, current_app, send_file, url_for
from flask_login import login_required, current_user
from .models import Book, Genre, Bookmark, Like, Comment, db
from .forms import BookUploadForm, BookUpdateForm
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict


books_bp = Blueprint('books', __name__)

@books_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_book():
    """Загрузка новой книги"""
    if request.method == 'POST':
        # Создаем MultiDict для формы
        form_data = MultiDict(request.form)
        form_data.update(request.files)
        
        form = BookUploadForm(form_data)
        
        if form.validate():
            book_file = request.files['book_file']
            cover_file = request.files.get('cover_image')
            
            # Сохранение файлов
            book_filename = secure_filename(book_file.filename)
            book_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'books', book_filename)
            book_file.save(book_path)
            
            cover_path = None
            if cover_file:
                cover_filename = secure_filename(cover_file.filename)
                cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers', cover_filename)
                cover_file.save(cover_path)
            
            # Создание книги
            new_book = Book(
                title=form.title.data,
                description=form.description.data,
                author_id=current_user.id,
                file_path=book_path,
                cover_image=cover_path
            )
            
            # Добавление жанров
            for genre_id in form.genres.data:
                genre = Genre.query.get(genre_id)
                if genre:
                    new_book.genres.append(genre)
            
            db.session.add(new_book)
            db.session.commit()
            
            flash('Книга успешно загружена', 'success')
            return redirect(url_for('books.list_books'))
        
        # Обработка ошибок валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
        
        return render_template('books/book_upload.html', form=form)
    
    form = BookUploadForm()
    return render_template('books/book_upload.html', form=form)

@books_bp.route('/', methods=['GET'])
def list_books():
    """Список книг с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    genre_id = request.args.get('genre', type=int)
    
    query = Book.query
    if genre_id:
        query = query.filter(Book.genres.any(id=genre_id))
    
    books = query.paginate(page=page, per_page=per_page)
    
    # Преобразование книг с полным путем к обложке
    book_list = []
    for book in books.items:
        book_data = {
            'id': book.id,
            'title': book.title,
            'description': book.description,
            'cover_image': book.cover_image
            }
        book_list.append(book_data)
    
    return render_template('books/book_list.html', 
        books=book_list, 
        pagination=books
    )

@books_bp.route('/<int:book_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def book_details(book_id):
    """Детали, обновление и удаление книги"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'GET':
        return render_template('books/book_detail.html', book=book)
    
    elif request.method == 'POST':
        # Проверка прав на редактирование
        if book.author_id != current_user.id:
            flash('Недостаточно прав', 'error')
            return redirect(url_for('books.book_details', book_id=book_id))
        
        form = BookUpdateForm(request.form)
        if form.validate():
            book.title = form.title.data
            book.description = form.description.data
            
            # Обновление жанров
            book.genres.clear()
            for genre_id in form.genres.data:
                genre = Genre.query.get(genre_id)
                if genre:
                    book.genres.append(genre)
            
            db.session.commit()
            
            flash('Книга обновлена', 'success')
            return redirect(url_for('books.book_details', book_id=book_id))
        
        # Обработка ошибок валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
        
        return render_template('books/book_detail.html', book=book, form=form)
    
    elif request.method == 'DELETE':
        # Проверка прав на удаление
        if book.author_id != current_user.id:
            flash('Недостаточно прав', 'error')
            return redirect(url_for('books.list_books'))
        
        db.session.delete(book)
        db.session.commit()
        
        flash('Книга удалена', 'success')
        return redirect(url_for('books.list_books'))

@books_bp.route('/<int:book_id>/bookmark', methods=['POST', 'DELETE'])
@login_required
def manage_bookmark(book_id):
    """Управление закладками"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        
        # Проверка/создание закладки
        bookmark = Bookmark.query.filter_by(
            user_id=current_user.id, 
            book_id=book_id
        ).first()
        
        if bookmark:
            bookmark.page = page
        else:
            bookmark = Bookmark(
                user_id=current_user.id, 
                book_id=book_id, 
                page=page
            )
            db.session.add(bookmark)
        
        db.session.commit()
        
        flash('Закладка сохранена', 'success')
        return redirect(url_for('books.book_details', book_id=book_id))
    
    elif request.method == 'DELETE':
        # Удаление закладки
        bookmark = Bookmark.query.filter_by(
            user_id=current_user.id, 
            book_id=book_id
        ).first()
        
        if bookmark:
            db.session.delete(bookmark)
            db.session.commit()
        
        flash('Закладка удалена', 'success')
        return redirect(url_for('books.book_details', book_id=book_id))

@books_bp.route('/<int:book_id>/read', methods=['GET'])
@login_required
def read_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Получение или создание закладки
    bookmark = Bookmark.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id
    ).first()
    
    # Создание закладки, если ее нет
    if not bookmark:
        bookmark = Bookmark(
            user_id=current_user.id, 
            book_id=book_id, 
            page=1
        )
        db.session.add(bookmark)
        db.session.commit()
    
    return render_template('books/book_reader.html', 
        book=book, 
        bookmark=bookmark
    )


@books_bp.route('/<int:book_id>/pdf', methods=['GET'])
@login_required
def serve_pdf(book_id):
    book = Book.query.get_or_404(book_id)
    file_path = os.path.abspath(book.file_path)
    
    return send_file(
        file_path, 
        mimetype='application/pdf',
        as_attachment=False
    )
