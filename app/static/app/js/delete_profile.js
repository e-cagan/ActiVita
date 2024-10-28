document.addEventListener("DOMContentLoaded", function() {
    const deleteProfileButton = document.querySelector(".btn-outline-danger");

    deleteProfileButton.addEventListener("click", function(e) {
        e.preventDefault();

        fetch("delete_profile/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Profile image deleted successfully!");
                const profileImage = document.querySelector('.profile-image');
                profileImage.src = "{% static 'app/img/default_profile.jpg' %}";  // Default image ile değiştir
            } else {
                alert("Failed to delete profile image: " + data.message);
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
