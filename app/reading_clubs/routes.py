from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.books.models import ClubMembers, ReadingClub, ClubDiscussion, db

reading_clubs_bp = Blueprint('reading_clubs', __name__)

@reading_clubs_bp.route('/')
def index():
    """Список читательских клубов"""
    clubs = ReadingClub.query.all()
    return render_template('reading_clubs/index.html', clubs=clubs)

@reading_clubs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_club():
    """Создание нового читательского клуба"""
    if request.method == 'POST':
        new_club = ReadingClub(
            name=request.form['name'],
            description=request.form['description'],
            creator_id=current_user.id
        )
        db.session.add(new_club)
        
        db.session.commit()
        
        # Автоматическое вступление создателя в клуб
        club_member = ClubMembers(
            user_id=current_user.id,
            club_id=new_club.id
        )
        db.session.add(club_member)
        
        db.session.commit()
        
        flash('Клуб успешно создан', 'success')
        return redirect(url_for('reading_clubs.club_details', club_id=new_club.id))
    
    return render_template('reading_clubs/create.html')

@reading_clubs_bp.route('/<int:club_id>/join')
@login_required
def join_club(club_id):
    """Вступление в читательский клуб"""
    club = ReadingClub.query.get_or_404(club_id)
    
    # Проверка, не состоит ли уже пользователь в клубе
    existing_membership = ClubMembers.query.filter_by(
        user_id=current_user.id, 
        club_id=club_id
    ).first()
    
    if existing_membership:
        flash('Вы уже состоите в этом клубе', 'warning')
        return redirect(url_for('reading_clubs.club_details', club_id=club_id))
    
    # Создание новой записи о членстве
    club_member = ClubMembers(
        user_id=current_user.id,
        club_id=club_id
    )
    db.session.add(club_member)
    db.session.commit()
    
    flash(f'Вы присоединились к клубу "{club.name}"', 'success')
    return redirect(url_for('reading_clubs.club_details', club_id=club_id))

@reading_clubs_bp.route('/<int:club_id>/leave')
@login_required
def leave_club(club_id):
    """Выход из читательского клуба"""
    club = ReadingClub.query.get_or_404(club_id)
    
    # Проверка, состоит ли пользователь в клубе
    club_membership = ClubMembers.query.filter_by(
        user_id=current_user.id, 
        club_id=club_id
    ).first()
    
    if not club_membership:
        flash('Вы не состоите в этом клубе', 'warning')
        return redirect(url_for('reading_clubs.club_details', club_id=club_id))
    
    # Удаление членства
    db.session.delete(club_membership)
    db.session.commit()
    
    flash(f'Вы вышли из клуба "{club.name}"', 'info')
    return redirect(url_for('reading_clubs.index'))

@reading_clubs_bp.route('/<int:club_id>')
def club_details(club_id):
    """Детали читательского клуба"""
    club = ReadingClub.query.get_or_404(club_id)
    discussions = ClubDiscussion.query.filter_by(club_id=club_id).all()
    
    # Проверка членства текущего пользователя
    is_member = False
    if current_user.is_authenticated:
        is_member = ClubMembers.query.filter_by(
            user_id=current_user.id, 
            club_id=club_id
        ).first() is not None
    
    return render_template(
        'reading_clubs/details.html', 
        club=club, 
        discussions=discussions,
        is_member=is_member
    )

