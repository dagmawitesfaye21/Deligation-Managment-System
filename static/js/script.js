document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    document.querySelector('#sidebarCollapse').addEventListener('click', function() {
        document.querySelector('#sidebar').classList.toggle('active');
    });
    
    // File input preview (optional)
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'No file selected';
            const label = e.target.previousElementSibling;
            if (label.tagName === 'LABEL') {
                label.textContent = fileName;
            }
        });
    });
});