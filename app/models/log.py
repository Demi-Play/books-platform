from app import db

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)  # Тип действия: 'publish', 'reject', 'update'
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    moderator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Модератор, который выполнил действие
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    book = db.relationship('Book', backref='logs')
    moderator = db.relationship('User', backref='logs')

    def __repr__(self):
        return f'<LogEntry {self.action_type} for Book ID {self.book_id} by Moderator ID {self.moderator_id}>'
