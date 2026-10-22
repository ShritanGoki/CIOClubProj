// CIO Clearinghouse — Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Fetch unread message count
    updateUnreadCount();
    setInterval(updateUnreadCount, 30000); // Poll every 30 seconds
});

function updateUnreadCount() {
    const badge = document.getElementById('unread-badge');
    if (!badge) return;

    fetch('/messages/unread-count/')
        .then(response => {
            if (!response.ok) return;
            return response.json();
        })
        .then(data => {
            if (!data) return;
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }
        })
        .catch(() => {});
}

// Bookmark toggle with CSRF
function toggleBookmark(slug, element) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        window.location.href = `/cios/${slug}/bookmark/`;
        return;
    }

    fetch(`/cios/${slug}/bookmark/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
    }).then(() => {
        window.location.reload();
    });
}
