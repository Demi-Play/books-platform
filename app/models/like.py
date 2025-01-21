from app import db

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    user = db.relationship('User', backref='likes')
    book = db.relationship('Book', backref='likes')

    def __repr__(self):
        return f'<Like User {self.user_id} Book {self.book_id}>'

