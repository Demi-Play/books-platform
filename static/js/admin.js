function openBlockModal(userId) {
    const modal = document.getElementById('blockModal');
    const userIdInput = document.getElementById('blockUserId');
    const blockForm = document.getElementById('blockForm');
    
    userIdInput.value = userId;
    modal.style.display = 'block';
}

function closeBlockModal() {
    const modal = document.getElementById('blockModal');
    modal.style.display = 'none';
}


