/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

  async function loginUser(email, password) {
      const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password })
      });
      if (!response.ok){
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Server Error : ${response.status}`);
      }
      return await response.json();
  }

  document.addEventListener('DOMContentLoaded', () => {
      const loginForm = document.getElementById('login-form');
      const placeId = getPlaceIdFromURL();
      const token = getCookie('token');
      const addReviewSection = document.getElementById('add-review');
      
      if(window.location.pathname.includes('place.html')){
        if (!placeId) {
          window.location.href = 'index.html';
          return;
       }

      if (addReviewSection) {
        addReviewSection.style.display = token ? 'block' : 'none';
      }
      fetchPlaceDetails(placeId, token)
    }


      if (loginForm) {
          loginForm.addEventListener('submit', async (event) => {
              event.preventDefault();
              const email = document.getElementById('email').value;
              const password = document.getElementById('password').value;
              const submitBtn = loginForm.querySelector('button[type="submit"]'); // Disable button during sending (visual feedback)
              if (submitBtn) submitBtn.disabled = true;

              try{
                const data = await loginUser(email, password);
                if (data && data.access_token) {
                  document.cookie = `token=${data.access_token}; path=/; SameSite=Lax`;
                  window.location.href = 'index.html'
                }
              } catch (error){
                console.error('Login Error:', error.message);
                alert('Login failed :' + error.message);
                if (submitBtn) submitBtn.disabled = false
              }
          });
      }
      checkAuthentification();
      setupPriceFilter();
  });

  function getCookie(name){
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

async function fetchPlaces(token) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const places = await response.json();
            displayPlaces(places);
        } else {
            console.error('Place fetching Error');
        }
    } catch (error) {
        console.error('Server Error :', error);
    }
}
  function checkAuthentification(){
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token){
      if (loginLink) loginLink.style.display = 'block';
    } else {
      if (loginLink) loginLink.style.display = 'none';
      fetchPlaces(token);
    }
    }

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;
    
    placesList.innerHTML = '';
    places.forEach(place => {
        const placeCard = document.createElement('div');
        placeCard.classList.add('place-card');
        
        const placePrice = place.price; 
        placeCard.setAttribute('data-price', placePrice);

        placeCard.innerHTML = `
            <h3>${place.title}</h3>
            <p>${place.description || 'No description available'}</p>
            <p><strong>Price:</strong> $${placePrice} / night</p>
            <p><strong>Location:</strong> Lat: ${place.latitude}, Long: ${place.longitude}</p>
            <button class="view-details-btn" onclick="window.location.href='place.html?id=${place.id}'">View Details</button>
        `;
        placesList.appendChild(placeCard);
    });
}

    function setupPriceFilter() {
      const filter = document.getElementById('price-filter');
      if (!filter) return;
      const options = [
        { value: 'all', text: 'All' },
        { value: '10', text: '$10' },
        { value: '50', text: '$50'},
        { value: '100', text: '$100' }
      ];

      options.forEach(opt => {
        const optionElement = document.createElement('option');
        optionElement.value = opt.value;
        optionElement.textContent = opt.text;
        filter.appendChild(optionElement);
      });

      filter.addEventListener('change', (event) => {
        const maxPrice = event.target.value;
        const cards = document.querySelectorAll('.place-card');

        cards.forEach(card => {
          const price = parseFloat(card.getAttribute('data-price'));
          if (maxPrice === 'all' || price <= parseFloat(maxPrice)) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        });
      });
    }

    function getPlaceIdFromURL(){
      const params = new URLSearchParams(window.location.search);
      return params.get('id');
    }

    async function fetchPlaceDetails(placeId, token) {
      const headers = { 'Content-Type': 'application/json' };
      if (token){
        headers['Authorization'] = `Bearer ${token}`;
      }

      try {
        const response = await fetch (`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
          method: 'GET',
          headers: headers
        });

        if (response.ok) {
          const place = await response.json();
          displayPlacesDetails(place);
        } else {
          console.error ('Failed to fetch place details');
        }
      } catch(error) {
        console.error('Error: ', error);
      }
    }

    function displayPlacesDetails(place) {
      const container = document.getElementById('place-details');
      if (!container) return;

      container.innerHTML = `
      <div class="place-info">
            <h1>${place.title}</h1>
            <p><strong>Price per night:</strong> $${place.price}</p>
            <p><strong>Description:</strong> ${place.description}</p>
            <p><strong>Location:</strong> Lat: ${place.latitude}, Long: ${place.longitude}</p>
            <p><strong>Host:</strong> ${place.owner_name || 'Host information not available'}</p>
        </div>

        <div class="place-amenities">
            <h3>Amenities</h3>
            <ul id="amenities-list">
                ${place.amenities.map(a => `<li>${a.name}</li>`).join('')}
            </ul>
        </div>

        <div class="reviews-section">
            <h3>Reviews</h3>
            <div id="reviews-list">
                ${place.reviews && place.reviews.length > 0 
                    ? place.reviews.map(review => `
                        <div class="review-card">
                            <p><strong>${review.user_name}:</strong> ${review.text}</p>
                            <p>Rating: ${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</p>
                        </div>
                    `).join('') 
                    : '<p>No reviews yet.</p>'}
            </div>
        </div>
    `;
}