document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            content.style.display = content.style.display === 'block' ? 'none' : 'block';
        });
    });

    const modal = document.getElementById('confirmation-modal');
    const saveButton = document.getElementById('save-privacy-settings');
    const closeButton = document.querySelector('.close-button');
    const confirmSave = document.getElementById('confirm-save');
    const cancelSave = document.getElementById('cancel-save');

    saveButton.addEventListener('click', (e) => {
        e.preventDefault();
        modal.style.display = 'block';
    });

    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    confirmSave.addEventListener('click', () => {
        modal.style.display = 'none';
        alert('Settings saved successfully!');
    });

    cancelSave.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});
