document.addEventListener("DOMContentLoaded", function() {
    const searchForm = document.querySelector('form[role="search"]');
    const searchInput = document.querySelector('.search-bar');
    const searchResults = document.getElementById('search-results');
    const mainContent = document.getElementById('main-content');
    const backButton = document.getElementById('back-button');

    searchForm.addEventListener("submit", function(event) {
        event.preventDefault();  // Formun varsayılan submit olayını engelle

        const query = searchInput.value;  // Arama çubuğundaki değeri al

        // Fetch API ile AJAX isteği yap
        fetch(searchForm.action, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
                "Content-Type": "application/x-www-form-urlencoded",  // Form-data için uygun Content-Type
            },
            body: `query=${encodeURIComponent(query)}`
        })
        .then(response => response.json())  // JSON formatında yanıt bekle
        .then(data => {
            // Arama sonuçlarını göster
            searchResults.innerHTML = "";  // Önceki sonuçları temizle
            mainContent.style.display = 'none';  // Ana içeriği gizle
            searchResults.style.display = 'block';  // Arama sonuçlarını göster
            backButton.style.display = 'block';

            if (data.results.length > 0) {
                // Sonuçları ekrana bas
                data.results.forEach(function(result) {
                    // Dinamik kart oluşturma fonksiyonu ile her bir etkinlik kartını oluştur
                    const eventCard = createEventCard(result);
                    searchResults.appendChild(eventCard);  // Oluşan kartı sonuçlara ekle
                });
            } else {
                const noResults = document.createElement("p");
                noResults.textContent = `No results for ${query}`;
                searchResults.appendChild(noResults);
            }
        })
        .catch(error => {
            console.error("An error occurred:", error);
        });
    });

    backButton.onclick = () => {
        searchResults.style.display = 'none';
        backButton.style.display = 'none';
        mainContent.style.display = 'block';
    }
});

// Dinamik kart oluşturma fonksiyonu
function createEventCard(event) {
    const card = document.createElement('div');
    card.classList.add('col-sm-6', 'mb-4', 'd-flex');
    card.setAttribute('id', 'event');
    card.setAttribute('data-event-id', event.id || "");  // Varsayılan boş dize

    card.innerHTML = `
      <div class="card w-100 d-flex flex-column">
        <div class="card-header text-center">
          <div class="d-flex justify-content-between align-items-center">
            <strong>${event.title || "Başlık Bulunamadı"}</strong>
            ${event.organizer === 'user1' ? `
              <div class="buttons d-inline-flex">
                <button type="button" class="btn btn-outline-success edit-event-btn" 
                  data-bs-toggle="modal" data-bs-target="#editEventModal"
                  data-event-id="${event.id || ""}" 
                  data-event-title="${event.title || ""}" 
                  data-event-description="${event.description || ""}" 
                  data-event-date="${event.date || ""}"
                  data-event-location="${event.location || ""}">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button type="button" class="btn btn-outline-danger delete-event-btn"
                  data-bs-toggle="modal" data-bs-target="#deleteEventModal"
                  data-event-id="${event.id || ""}">
                  <i class="fa-solid fa-x"></i>
                </button>
              </div>` : ''}
          </div>
        </div>
        <div class="card-body d-flex flex-column flex-grow-1">
          <h6 class="card-subtitle mb-2 text-body-secondary">Organized by <strong>${event.organizer || "Bilinmiyor"}</strong> until <strong>${event.date || "Bilinmiyor"}</strong>.</h6>
          <h6 class="card-subtitle mb-2 text-body-secondary">Category: ${event.category || "Bilinmiyor"}</h6>
          <h6 class="card-subtitle mb-2 text-body-secondary">Location: ${event.location || "Bilinmiyor"}</h6>
          <h6 class="card-subtitle mb-2 text-body-secondary">Target Donation: $${event.target_donation || "0"}</h6>
          <br>
          <p class="card-text">${event.description || "Açıklama bulunamadı."}</p>
          <div class="progress">
            <div class="progress-bar bg-primary" style="width: ${event.donation_progress || 0}%;">
              %${event.donation_progress || 0}
            </div>
          </div>
        </div>
        <div class="card-footer text-center">
          ${event.organizer !== 'user1' ? `
            <a href="/make_donation/${event.id || ""}" class="card-link btn btn-outline-primary">Donate</a>
            ${event.is_participated ? `
              <form action="/departicipate_event/${event.id || ""}" method="post">
                <button class="btn btn-outline-danger">Departicipate</button>
              </form>` : `
              <form action="/participate_event/${event.id || ""}" method="post">
                <button class="btn btn-outline-success">Participate</button>
              </form>`}
          ` : ''}
          <a href="/event_details/${event.id || ""}" class="btn btn-outline-info">Details</a>
        </div>
      </div>
    `;

    return card;
}

// Helper function to get csrf token
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
