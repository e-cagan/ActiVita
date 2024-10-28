document.addEventListener('DOMContentLoaded', function() {
    const deleteEventModal = document.getElementById('deleteEventModal');
    const deleteEventForm = document.getElementById('deleteEventForm');

    // Modal açma fonksiyonu
    document.querySelectorAll('.delete-event-btn').forEach(button => {
        button.addEventListener('click', function () {
            const eventId = this.dataset.eventId;
            const deleteUrl = this.dataset.deleteUrl;

            // Form içindeki gizli alanı güncelle
            deleteEventForm.querySelector('#event_id').value = eventId;
            deleteEventForm.action = deleteUrl;

            // Modalı aç
            new bootstrap.Modal(deleteEventModal).show();
        });
    });

    // Delete butonuna dinleyici ekle
    document.getElementById('deleteYesButton').addEventListener('click', function (e) {
        e.preventDefault(); // Sayfanın yeniden yüklenmesini engelle

        const formData = new FormData(deleteEventForm);
        const deleteUrl = deleteEventForm.action;

        // AJAX isteği gönder
        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Sayfayı yenile veya öğeyi DOM'dan kaldır
                location.reload();
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

// Helper function to take csrf token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
