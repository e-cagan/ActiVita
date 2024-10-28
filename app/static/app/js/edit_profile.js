document.addEventListener("DOMContentLoaded", function() {
    const editProfileForm = document.getElementById("editProfileForm");

    editProfileForm.addEventListener("submit", function(e) {
        e.preventDefault();

        const formData = new FormData(editProfileForm);
        
        fetch("edit_profile/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                location.reload();  // Dinamik olarak resmi değiştirebilirsin, reload zorunlu değil
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
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
