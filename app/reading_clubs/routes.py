from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.books.models import ReadingClub, ClubDiscussion, db

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
        return redirect(url_for('reading_clubs.index'))
    
    return render_template('reading_clubs/create.html')

@reading_clubs_bp.route('/<int:club_id>')
def club_details(club_id):
    """Детали читательского клуба"""
    club = ReadingClub.query.get_or_404(club_id)
    discussions = ClubDiscussion.query.filter_by(club_id=club_id).all()
    
    return render_template(
        'reading_clubs/details.html', 
        club=club, 
        discussions=discussions
    )
