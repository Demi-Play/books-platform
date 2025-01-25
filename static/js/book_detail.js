function toggleLike(bookId) {
    fetch(`/books/${bookId}/like`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            const likeButton = document.getElementById('like-button');
            likeButton.textContent = `❤️ ${data.total_likes}`;
            likeButton.classList.toggle('liked', data.liked);
        });
}

function addComment(event, bookId) {
    event.preventDefault();
    const commentText = document.getElementById('comment-text').value;
    
    // Создание FormData и добавление данных
    const formData = new FormData();
    formData.append('text', commentText);
    
    fetch(`/books/${bookId}/comments`, {
        method: 'POST',
        body: formData  // Используем formData корректно
    })
    .then(response => {
        if (!response.ok) {
            // Обработка ошибок
            return response.json().then(errorData => {
                throw new Error(errorData.error);
            });
        }
        return response.json();
    })
    .then(data => {
        // Добавление нового комментария в список
        const commentsList = document.getElementById('comments-list');
        const newComment = document.createElement('div');
        newComment.innerHTML = `
            <p>${data.text}</p>
            <small>${data.author} | ${data.created_at}</small>
        `;
        commentsList.prepend(newComment);
        document.getElementById('comment-text').value = '';
    })
    .catch(error => {
        // Вывод ошибки пользователю
        alert(error.message);
    });
}

function editComment(commentId) {
    const commentElement = document.getElementById(`comment-${commentId}`);
    const currentText = commentElement.querySelector('p').textContent;
    
    commentElement.innerHTML = `
        <textarea id="edit-comment-${commentId}">${currentText}</textarea>
        <button onclick="saveComment(${commentId})">Сохранить</button>
    `;
}

function saveComment(commentId) {
    const newText = document.getElementById(`edit-comment-${commentId}`).value;
    
    fetch(`/comments/${commentId}`, {
        method: 'PUT',
        body: new FormData().append('text', newText)
    })
    .then(response => response.json())
    .then(data => {
        const commentElement = document.getElementById(`comment-${commentId}`);
        commentElement.innerHTML = `
            <p>${data.text}</p>
            <small>Вы | Только что</small>
            <div class="comment-actions">
                <button onclick="editComment(${commentId})">Редактировать</button>
                <button onclick="deleteComment(${commentId})">Удалить</button>
            </div>
        `;
    });
}

function deleteComment(commentId) {
    if (confirm('Вы уверены, что хотите удалить комментарий?')) {
        fetch(`/comments/${commentId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(() => {
            const commentElement = document.getElementById(`comment-${commentId}`);
            commentElement.remove();
        });
    }
}



function deleteBook(bookId) {
    if(confirm('Вы уверены, что хотите удалить книгу?')) {
        fetch(`/books/${bookId}`, {
            method: 'DELETE'
        }).then(response => {
            if(response.ok) {
                window.location.href = "{{ url_for('books.list_books') }}";
            }
        });
    }
}

function toggleBookmark(bookId, currentPage) {
    const bookmarkButton = document.getElementById('bookmark-button');
    const method = bookmarkButton.classList.contains('bookmark-active') ? 'DELETE' : 'POST';
    
    const formData = new FormData();
    formData.append('page', currentPage);

    fetch(`/books/${bookId}/bookmark`, {
        method: method,
        body: method === 'POST' ? formData : null
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bookmarkButton.classList.toggle('bookmark-active');
            bookmarkButton.textContent = method === 'POST' 
                ? 'Удалить закладку' 
                : 'Добавить закладку';
            
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось обработать закладку');
    });
}