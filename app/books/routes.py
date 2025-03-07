from flask import Blueprint, abort, flash, redirect, request, jsonify, render_template, current_app, send_file, url_for
from flask_login import login_required, current_user
from .models import Book, Genre, Bookmark, Like, Comment, db
from .forms import BookUploadForm, BookUpdateForm
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict
from sqlalchemy.orm import joinedload
from app.auth.models import UserRole
books_bp = Blueprint('books', __name__)

@books_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_book():
    """Загрузка новой книги"""
    if request.method == 'POST':
        form_data = MultiDict(request.form)
        form_data.update(request.files)
        
        form = BookUploadForm(form_data)
        
        if form.validate():
            book_file = request.files['book_file']
            # cover_file = request.files.get('cover_image')
            
            # Получение имени файла
            book_filename = secure_filename(book_file.filename)
            # cover_filename = secure_filename(cover_file.filename) if cover_file else None
            
            # Создание директорий
            os.makedirs(os.path.join(current_app.root_path, 'uploads', 'books'), exist_ok=True)
            # os.makedirs(os.path.join(current_app.root_path, 'uploads', 'covers'), exist_ok=True)
            
            # Сохранение файлов
            book_save_path = os.path.join(current_app.root_path, 'uploads', 'books', book_filename)
            book_file.save(book_save_path)
            
            # Сохранение обложки, если она есть
            # cover_save_path = None
            # if cover_file:
            #     cover_save_path = os.path.join(current_app.root_path, 'uploads', 'covers', cover_filename)
            #     cover_file.save(cover_save_path)
            
            # Создание книги с относительным путем
            new_book = Book(
                title=form.title.data,
                description=form.description.data,
                author_id=current_user.id,
                file_path=os.path.join('uploads', 'books', book_filename),
                # cover_image=os.path.join('uploads', 'covers', cover_filename) if cover_filename else None
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
        
        return render_template('books/book_upload.html', form=form, UserRole=UserRole)
    
    form = BookUploadForm()
    return render_template('books/book_upload.html', form=form, UserRole=UserRole)

@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Проверка прав доступа
    if book.author_id != current_user.id:
        flash('Недостаточно прав для редактирования', 'error')
        return redirect(url_for('books.book_details', book_id=book_id))
    
    form = BookUpdateForm(obj=book)
    
    if request.method == 'POST':
        form = BookUpdateForm(request.form)
        
        if form.validate():
            # Ручное обновление полей вместо populate_obj
            book.title = form.title.data
            book.description = form.description.data
            
            # Обработка жанров
            book.genres.clear()
            for genre_id in form.genres.data:
                genre = Genre.query.get(genre_id)
                if genre:
                    book.genres.append(genre)
            
            db.session.commit()
            
            flash('Книга успешно обновлена', 'success')
            return redirect(url_for('books.book_details', book_id=book_id))
        
        # Обработка ошибок валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
    
    return render_template('books/book_edit.html', form=form, book=book, UserRole=UserRole)

@books_bp.route('/', methods=['GET'])
def list_books():
    """Список книг с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    genre_id = request.args.get('genre', type=int)
    
    
    books = Book.query.filter_by(status='approved').all()
    
    # Преобразование книг с полным путем к обложке
    book_list = []
    for book in books:
        book_data = {
            'id': book.id,
            'title': book.title,
            'description': book.description,
            'cover_image': book.cover_image
            }
        book_list.append(book_data)
    
    return render_template('books/book_list.html', 
        books=book_list, 
        pagination=books,
        UserRole=UserRole
    )

@books_bp.route('/<int:book_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def book_details(book_id):
    """Детали, обновление и удаление книги"""
    book = Book.query.options(
        joinedload(Book.comments).joinedload(Comment.username)
    ).get_or_404(book_id)
    
    # Получение закладки пользователя для этой книги
    user_bookmark = None
    current_user_liked = False
    if current_user.is_authenticated:
        user_bookmark = Bookmark.query.filter_by(
            user_id=current_user.id, 
            book_id=book_id
        ).first()
        current_user_liked = Like.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first() is not None
    
    if request.method == 'GET':
        return render_template('books/book_detail.html', 
            book=book, 
            user_bookmark=user_bookmark,
            current_user_liked=current_user_liked,
            UserRole=UserRole
        )
    
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
        
        return render_template('books/book_detail.html', 
            book=book, 
            form=form, 
            user_bookmark=user_bookmark,
            current_user_liked=current_user_liked,
            UserRole=UserRole
        )
    
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
        
        return jsonify({
            'success': True, 
            'message': 'Закладка сохранена',
            'page': page
        })
    
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
            'success': True, 
            'message': 'Закладка удалена'
        })


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
        bookmark=bookmark,
        UserRole=UserRole
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

# Комментарии

@books_bp.route('/<int:book_id>/like', methods=['POST'])
@login_required
def toggle_like(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Проверка существующего лайка
    existing_like = Like.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id
    ).first()
    
    if existing_like:
        # Удаление лайка
        db.session.delete(existing_like)
    else:
        # Добавление лайка
        new_like = Like(
            user_id=current_user.id, 
            book_id=book_id
        )
        db.session.add(new_like)
    
    db.session.commit()
    
    return jsonify({
        'total_likes': len(book.likes),
        'liked': existing_like is None
    })

@books_bp.route('/<int:book_id>/comments', methods=['POST'])
@login_required
def add_comment(book_id):
    book = Book.query.get_or_404(book_id)
    
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'Комментарий не может быть пустым'}), 400
    
    new_comment = Comment(
        user_id=current_user.id,
        book_id=book_id,
        text=text
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        'id': new_comment.id,
        'text': new_comment.text,
        'author': current_user.username,
        'created_at': new_comment.created_at.isoformat()
    })

@books_bp.route('/comments/<int:comment_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Проверка прав на изменение комментария
    if comment.user_id != current_user.id:
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    if request.method == 'PUT':
        # Редактирование комментария
        new_text = request.form.get('text')
        if not new_text:
            return jsonify({'error': 'Комментарий не может быть пустым'}), 400
        
        comment.text = new_text
        db.session.commit()
        
        return jsonify({
            'id': comment.id,
            'text': comment.text
        })
    
    elif request.method == 'DELETE':
        # Удаление комментария
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'success': True})
