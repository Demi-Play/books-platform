document.addEventListener('DOMContentLoaded', function() {
    const approveButtons = document.querySelectorAll('.approve-book');
    const rejectButtons = document.querySelectorAll('.reject-book');

    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            approveBook(bookId);
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            rejectBook(bookId);
        });
    });

    function approveBook(bookId) {
        fetch(`/moderator/book/${bookId}/approve`, {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                const bookCard = document.querySelector(`.approve-book[data-book-id="${bookId}"]`).closest('.book-card');
                bookCard.remove();
                alert('Книга одобрена');
                window.location.reload()
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Не удалось одобрить книгу');
            window.location.reload()
        });
    }

    function rejectBook(bookId) {
        fetch(`/moderator/book/${bookId}/reject`, {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                const bookCard = document.querySelector(`.reject-book[data-book-id="${bookId}"]`).closest('.book-card');
                bookCard.remove();
                alert('Книга отклонена');
                window.location.reload()
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Не удалось отклонить книгу');
            window.location.reload()
        });
    }
});