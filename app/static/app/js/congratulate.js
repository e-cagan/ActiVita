document.addEventListener("DOMContentLoaded", () => {
    const congratulateForm = document.getElementById('congratulate-form');
    
    // Tüm tebrik butonlarını seç
    document.querySelectorAll('.congratulate-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Varsayılan form gönderimini durdur
            const congratulatorId = this.dataset.congratulatorId; // Butonun veri niteliğinden kullanıcı id'sini al
            const userId = this.dataset.userId; // Butonun veri niteliğinden tebrik edilecek kullanıcı id'sini al
            const formData = new FormData(congratulateForm);

            // Fetch isteğini gönder
            fetch(`congratulate/${congratulatorId}/${userId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') // CSRF token'ı
                },
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "true") {
                    alert(data.message);
                } else {
                    alert("Bir hata oluştu. Lütfen tekrar deneyin.");
                }
            })
            .catch(error => console.error("Hata:", error));
        });
    });
});

// CSRF token'ı alma fonksiyonu
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
