from flask import Blueprint, render_template, redirect, url_for
from app import db
from app.models.log import LogEntry
from app.models.book import Book

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/logs', methods=['GET'])
def view_logs():
    logs = LogEntry.query.order_by(LogEntry.timestamp.desc()).all()
    return render_template('admin/logs.html', logs=logs)

@bp.route('/logs/<int:log_id>/revert', methods=['POST'])
def revert_action(log_id):
    log_entry = LogEntry.query.get_or_404(log_id)

    if log_entry.reverted:
        return redirect(url_for('admin.view_logs'))

    if log_entry.action == 'Created':
        # Удаляем книгу
        book_to_delete = Book.query.get(log_entry.book_id)
        if book_to_delete:
            db.session.delete(book_to_delete)

    elif log_entry.action == 'Edited':
        # Здесь можно добавить логику восстановления предыдущей версии книги (если есть резервные копии).
        pass

    elif log_entry.action == 'Deleted':
        # Восстановление удаленной книги невозможно без резервной копии.
        pass

    log_entry.reverted = True
    db.session.commit()

    return redirect(url_for('admin.view_logs'))
