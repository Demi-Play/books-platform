from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, MultipleFileField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional

class BookUploadForm(FlaskForm):
    """Форма загрузки книги"""
    title = StringField('Название книги', [
        DataRequired(message='Обязательное поле'),
        Length(min=2, max=200, message='От 2 до 200 символов')
    ])
    description = TextAreaField('Описание', [
        Optional(),
        Length(max=1000, message='Максимум 1000 символов')
    ])
    book_file = FileField('Файл книги', [
        FileRequired(message='Файл книги обязателен'),
        FileAllowed(['pdf', 'epub', 'mobi'], message='Неподдерживаемый формат файла')
    ])
    # cover_image = FileField('Обложка', [
    #     Optional(),
    #     FileAllowed(['jpg', 'png', 'jpeg'], message='Только изображения')
    # ])
    genres = SelectMultipleField('Жанры', 
        coerce=int,
        validators=[Optional()]
    )

    def __init__(self, *args, **kwargs):
        """Динамическое заполнение жанров"""
        super().__init__(*args, **kwargs)
        from app.books.models import Genre
        self.genres.choices = [(genre.id, genre.name) for genre in Genre.query.all()]

class BookUpdateForm(FlaskForm):
    """Форма обновления книги"""
    title = StringField('Название книги', [
        Optional(),
        Length(min=2, max=200, message='От 2 до 200 символов')
    ])
    description = TextAreaField('Описание', [
        Optional(),
        Length(max=1000, message='Максимум 1000 символов')
    ])
    genres = SelectMultipleField('Жанры', 
        coerce=int,
        validators=[Optional()]
    )

    def __init__(self, *args, **kwargs):
        """Динамическое заполнение жанров"""
        super().__init__(*args, **kwargs)
        from app.books.models import Genre
        self.genres.choices = [(genre.id, genre.name) for genre in Genre.query.all()]

class CommentForm(FlaskForm):
    """Форма добавления комментария"""
    text = TextAreaField('Комментарий', [
        DataRequired(message='Комментарий не может быть пустым'),
        Length(max=500, message='Максимум 500 символов')
    ])
