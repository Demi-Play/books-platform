function toggleMembersList() {
    const membersList = document.getElementById('members-list');
    const toggleIcon = document.getElementById('members-toggle-icon');
    
    if (membersList.style.display === 'none') {
        membersList.style.display = 'block';
        toggleIcon.textContent = '▲';
    } else {
        membersList.style.display = 'none';
        toggleIcon.textContent = '▼';
    }
}