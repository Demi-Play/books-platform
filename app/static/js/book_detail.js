// Function to get CSRF token from meta tag
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Function to toggle like
function toggleLike(bookId) {
    fetch(`/books/${bookId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const likeButton = document.getElementById('like-button');
        likeButton.textContent = `❤️ ${data.total_likes}`;
        if (data.liked) {
            likeButton.classList.add('liked');
        } else {
            likeButton.classList.remove('liked');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при обработке лайка');
    });
}

// Function to add comment
function addComment(event, bookId) {
    event.preventDefault();
    
    const commentText = document.getElementById('comment-text').value;
    if (!commentText.trim()) {
        alert('Комментарий не может быть пустым');
        return;
    }

    const formData = new FormData();
    formData.append('text', commentText);
    formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);

    fetch(`/books/${bookId}/comments`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const commentsList = document.getElementById('comments-list');
        const newComment = document.createElement('div');
        newComment.className = 'comment';
        newComment.id = `comment-${data.id}`;
        
        const commentHTML = `
            <p>${data.text}</p>
            <small>${data.author} | ${new Date(data.created_at).toLocaleString()}</small>
            <div class="comment-actions">
                <button onclick="editComment(${data.id})" class="mui-btn mui-btn--small">Редактировать</button>
                <button onclick="deleteComment(${data.id})" class="mui-btn mui-btn--small mui-btn--danger">Удалить</button>
            </div>
        `;
        
        newComment.innerHTML = commentHTML;
        commentsList.insertBefore(newComment, commentsList.firstChild);
        document.getElementById('comment-text').value = '';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при добавлении комментария');
    });
}

// Function to edit comment
function editComment(commentId) {
    const commentElement = document.getElementById(`comment-${commentId}`);
    const currentText = commentElement.querySelector('p').textContent;
    
    const newText = prompt('Редактировать комментарий:', currentText);
    if (newText === null || newText.trim() === '') return;

    fetch(`/books/comments/${commentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ text: newText })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        commentElement.querySelector('p').textContent = data.text;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при редактировании комментария');
    });
}

// Function to delete comment
function deleteComment(commentId) {
    if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) return;

    fetch(`/books/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const commentElement = document.getElementById(`comment-${commentId}`);
        commentElement.remove();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при удалении комментария');
    });
} 