/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

  async function loginUser(email, password) {
      const response = await fetch('http://127.0.0.1:5500/api/v1/auth/login', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password })
      });
      if (!response.ok){
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Erreur serveur : ${response.status}`);
      }
      return await response.json();
  }

  document.addEventListener('DOMContentLoaded', () => {
      const loginForm = document.getElementById('login-form');

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
  });