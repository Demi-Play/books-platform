from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))  # Путь к изображению обложки
    content = db.Column(db.LargeBinary, nullable=False)  # Хранение содержимого книги
    file_name = db.Column(db.String(255))  # Имя загруженного файла книги
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_published = db.Column(db.Boolean, default=False)  # Статус публикации
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Кто обновил книгу
    version_number = db.Column(db.Integer, default=1)  # Номер версии

    updated_by = db.relationship('User', backref='updated_books')

    def __repr__(self):
        return f'<Book {self.title}>'

