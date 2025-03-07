from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.books.models import ClubMembers, ReadingClub, ClubDiscussion, Genre, Book
from app.books.models import db
from app.auth.models import UserRole

reading_clubs_bp = Blueprint('reading_clubs', __name__)

@reading_clubs_bp.route('/')
def index():
    """Список читательских клубов"""
    # Получаем все категории (жанры)
    categories = Genre.query.all()
    
    # Получаем выбранную категорию из параметров запроса
    category_id = request.args.get('category', type=int)
    
    # Получаем книги для выбранной категории
    if category_id:
        books = Book.query.filter(Book.genres.any(id=category_id)).all()
        selected_category = Genre.query.get(category_id)
    else:
        books = []
        selected_category = None
    
    return render_template(
        'reading_clubs/index.html', 
        books=books, 
        categories=categories,
        selected_category=selected_category,
        UserRole=UserRole
    )

@reading_clubs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_club():
    """Создание нового клуба"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        
        if not name:
            flash('Название клуба обязательно', 'error')
            return redirect(url_for('reading_clubs.create_club'))
        
        club = ReadingClub(
            name=name,
            description=description,
            id=category_id
        )
        db.session.add(club)
        
        # Добавляем создателя как администратора клуба
        membership = ClubMembers(
            user_id=current_user.id,
            club_id=club.id,
            is_admin=True
        )
        db.session.add(membership)
        
        try:
            db.session.commit()
            flash('Клуб успешно создан', 'success')
            return redirect(url_for('reading_clubs.club_details', club_id=club.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании клуба: {str(e)}', 'error')
    
    # Получаем список категорий для формы
    categories = Genre.query.all()
    return render_template(
        'reading_clubs/create.html',
        categories=categories,
        UserRole=UserRole
    )

@reading_clubs_bp.route('/<int:club_id>')
def club_details(club_id):
    """Детали клуба"""
    club = ReadingClub.query.get_or_404(club_id)
    discussions = club.discussions.order_by(ClubDiscussion.created_at.desc()).all()
    
    # Проверяем, является ли пользователь членом клуба
    is_member = False
    is_admin = False
    if current_user.is_authenticated:
        membership = ClubMembers.query.filter_by(
            user_id=current_user.id,
            club_id=club_id
        ).first()
        if membership:
            is_member = True
            is_admin = membership.is_admin
    
    return render_template(
        'reading_clubs/details.html',
        club=club,
        discussions=discussions,
        is_member=is_member,
        is_admin=is_admin,
        UserRole=UserRole
    )

@reading_clubs_bp.route('/<int:club_id>/join')
@login_required
def join_club(club_id):
    """Вступление в клуб"""
    club = ReadingClub.query.get_or_404(club_id)
    
    # Проверка, не является ли пользователь уже членом клуба
    existing_membership = ClubMembers.query.filter_by(
        user_id=current_user.id,
        club_id=club_id
    ).first()
    
    if existing_membership:
        flash('Вы уже являетесь членом этого клуба', 'warning')
        return redirect(url_for('reading_clubs.club_details', club_id=club_id))
    
    # Создание нового членства
    membership = ClubMembers(
        user_id=current_user.id,
        club_id=club_id,
        is_admin=False
    )
    db.session.add(membership)
    
    try:
        db.session.commit()
        flash(f'Вы успешно присоединились к клубу "{club.name}"', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при вступлении в клуб: {str(e)}', 'error')
    
    return redirect(url_for('reading_clubs.club_details', club_id=club_id))

@reading_clubs_bp.route('/<int:club_id>/leave')
@login_required
def leave_club(club_id):
    """Выход из клуба"""
    club = ReadingClub.query.get_or_404(club_id)
    
    # Проверка, является ли пользователь членом клуба
    membership = ClubMembers.query.filter_by(
        user_id=current_user.id,
        club_id=club_id
    ).first()
    
    if not membership:
        flash('Вы не состоите в этом клубе', 'warning')
        return redirect(url_for('reading_clubs.club_details', club_id=club_id))
    
    # Проверка, не является ли пользователь администратором
    if membership.is_admin:
        flash('Администратор не может покинуть клуб', 'error')
        return redirect(url_for('reading_clubs.club_details', club_id=club_id))
    
    # Удаление членства
    db.session.delete(membership)
    
    try:
        db.session.commit()
        flash(f'Вы вышли из клуба "{club.name}"', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при выходе из клуба: {str(e)}', 'error')
    
    return redirect(url_for('reading_clubs.index'))

@reading_clubs_bp.route('/<int:club_id>/discussion/create', methods=['GET', 'POST'])
@login_required
def create_discussion(club_id):
    """Создание нового обсуждения"""
    club = ReadingClub.query.get_or_404(club_id)
    
    # Проверка членства в клубе
    membership = ClubMembers.query.filter_by(
        user_id=current_user.id,
        club_id=club_id
    ).first()
    
    if not membership:
        flash('Вы должны быть членом клуба, чтобы создавать обсуждения', 'error')
        return redirect(url_for('reading_clubs.club_details', club_id=club_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('reading_clubs.create_discussion', club_id=club_id))
        
        discussion = ClubDiscussion(
            club_id=club_id,
            user_id=current_user.id,
            title=title,
            content=content
        )
        db.session.add(discussion)
        
        try:
            db.session.commit()
            flash('Обсуждение успешно создано', 'success')
            return redirect(url_for('reading_clubs.club_details', club_id=club_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании обсуждения: {str(e)}', 'error')
    
    return render_template(
        'reading_clubs/create_discussion.html',
        club=club,
        UserRole=UserRole
    )

