from app import db

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    page_number = db.Column(db.Integer)  # Номер страницы закладки

    user = db.relationship('User', backref='bookmarks')
    book = db.relationship('Book', backref='bookmarks')

    def __repr__(self):
        return f'<Bookmark User {self.user_id} Book {self.book_id} Page {self.page_number}>'
