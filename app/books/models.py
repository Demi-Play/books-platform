from datetime import datetime
from sqlalchemy.orm import relationship
from ..auth.models import db, User, UserRole

class Genre(db.Model):
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    books = db.relationship('Book', secondary='book_genres', back_populates='genres')

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Метаданные книги
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    published_at = db.Column(db.DateTime, default=datetime.now)
    
    # Файлы и обложка
    file_path = db.Column(db.String(255))
    cover_image = db.Column(db.String(255))
    
    status = db.Column(db.String(255), default='pending')

    # Связи
    genres = db.relationship('Genre', secondary='book_genres', back_populates='books')
    bookmarks = db.relationship('Bookmark', backref='book')
    likes = db.relationship('Like', backref='book')
    comments = db.relationship('Comment', backref='book')

class BookGenre(db.Model):
    __tablename__ = 'book_genres'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), primary_key=True)

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    page = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    username = db.relationship('User', backref='comment')
    

class ReadingClub(db.Model):
    __tablename__ = 'reading_clubs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    creator = db.relationship('User', backref='created_clubs')
    members = db.relationship('User', secondary='club_members', back_populates='reading_clubs')
    discussions = db.relationship('ClubDiscussion', backref='club')

class ClubMembers(db.Model):
    __tablename__ = 'club_members'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('reading_clubs.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.now)

class ClubDiscussion(db.Model):
    __tablename__ = 'club_discussions'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('reading_clubs.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    book = db.relationship('Book')
    messages = db.relationship('DiscussionMessage', backref='discussion')

class DiscussionMessage(db.Model):
    __tablename__ = 'discussion_messages'

    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('club_discussions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User')

class BookRecommendation(db.Model):
    __tablename__ = 'book_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    book = db.relationship('Book')
