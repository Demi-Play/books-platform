from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from .models import Book, Genre, Bookmark, Like, Comment, db
from .forms import BookUploadForm, BookUpdateForm
import os
from werkzeug.utils import secure_filename

books_bp = Blueprint('books', __name__)

@books_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_book():
    """Загрузка новой книги"""
    if request.method == 'POST':
        form = BookUploadForm(request.form, request.files)
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
            
            return jsonify({
                'status': 'success', 
                'message': 'Книга успешно загружена',
                'book_id': new_book.id
            }), 201
        
        return jsonify({
            'status': 'error', 
            'errors': form.errors
        }), 400
    
    return render_template('books/upload.html')

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
    
    return jsonify({
        'books': [
            {
                'id': book.id,
                'title': book.title,
                'description': book.description,
                'author': book.author.username,
                'cover': book.cover_image
            } for book in books.items
        ],
        'total_pages': books.pages,
        'current_page': books.page
    }), 200

@books_bp.route('/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def book_details(book_id):
    """Детали, обновление и удаление книги"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': book.id,
            'title': book.title,
            'description': book.description,
            'author': book.author.username,
            'genres': [genre.name for genre in book.genres],
            'cover': book.cover_image
        }), 200
    
    elif request.method == 'PUT':
        # Проверка прав на редактирование
        if book.author_id != current_user.id:
            return jsonify({
                'status': 'error', 
                'message': 'Недостаточно прав'
            }), 403
        
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
            
            return jsonify({
                'status': 'success', 
                'message': 'Книга обновлена'
            }), 200
        
        return jsonify({
            'status': 'error', 
            'errors': form.errors
        }), 400
    
    elif request.method == 'DELETE':
        # Проверка прав на удаление
        if book.author_id != current_user.id:
            return jsonify({
                'status': 'error', 
                'message': 'Недостаточно прав'
            }), 403
        
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Книга удалена'
        }), 200

@books_bp.route('/<int:book_id>/bookmark', methods=['POST', 'DELETE'])
@login_required
def manage_bookmark(book_id):
    """Управление закладками"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        page = request.json.get('page', 1)
        
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
        
        return jsonify({
            'status': 'success', 
            'message': 'Закладка сохранена'
        }), 200
    
    elif request.method == 'DELETE':
        # Удаление закладки
        bookmark = Bookmark.query.filter_by(
            user_id=current_user.id, 
            book_id=book_id
        ).first()
        
        if bookmark:
            db.session.delete(bookmark)
            db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Закладка удалена'
        }), 200
