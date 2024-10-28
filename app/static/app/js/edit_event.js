document.addEventListener('DOMContentLoaded', function() {
    const editEventForm = document.getElementById('editEventForm');
    const editModal = document.getElementById('editEventModal'); // Modal ID'si

    // Modal açma fonksiyonu
    document.querySelectorAll('.edit-event-btn').forEach(button => {
        button.addEventListener('click', function () {
            const eventId = this.dataset.eventId;
            const eventTitle = this.dataset.eventTitle;
            const eventDescription = this.dataset.eventDescription;
            const eventDate = this.dataset.eventDate;
            const eventLocation = this.dataset.eventLocation;
            const editUrl = this.dataset.editUrl;

            // Modal içindeki inputları doldur
            editEventForm.querySelector('#new_title').value = eventTitle;
            editEventForm.querySelector('#new_description').value = eventDescription;
            editEventForm.querySelector('#new_date').value = eventDate;
            editEventForm.querySelector('#new_location').value = eventLocation;
            editEventForm.querySelector('#event_id').value = eventId;

            // Formun action URL'sini güncelle
            editEventForm.action = editUrl;

            // Modalı aç
            new bootstrap.Modal(editModal).show();
        });
    });

    // Save butonuna dinleyici ekle
    document.getElementById('saveChanges').addEventListener('click', function (e) {
        e.preventDefault(); // Sayfanın yeniden yüklenmesini engelle
        const formData = new FormData(editEventForm);
        const editUrl = editEventForm.action;

        // AJAX isteği gönder
        fetch(editUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Yanıtı kontrol et
            if (data.success) {
                // Modalı kapat
                bootstrap.Modal.getInstance(editModal).hide();

                // Güncellenen etkinliği bul ve DOM'da güncelle
                const eventElement = document.querySelector(`[data-event-id="${data.event_id}"]`);
                if (eventElement) {
                    eventElement.querySelector('.event-title').textContent = data.new_title;
                    eventElement.querySelector('.event-description').textContent = data.new_description;
                    eventElement.querySelector('.event-date').textContent = data.new_date;
                    eventElement.querySelector('.event-location').textContent = data.new_location;
                }
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
