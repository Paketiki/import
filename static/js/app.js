const API_URL = '/api/v1';
let currentUser = null;
let currentToken = null;
let currentUserRole = null;
let allMovies = [];
let selectedMovieId = null;
let currentFilter = { pick: 'all', rating: 0 };
let favoritesSet = new Set();

// Init
document.addEventListener('DOMContentLoaded', () => {
  restoreSession();
  loadMovies();
});

// Theme toggle
function toggleTheme() {
  const body = document.body;
  if (body.classList.contains('theme-dark')) {
    body.classList.remove('theme-dark');
    body.classList.add('theme-light');
    localStorage.setItem('theme', 'light');
  } else {
    body.classList.remove('theme-light');
    body.classList.add('theme-dark');
    localStorage.setItem('theme', 'dark');
  }
}

// Restore theme from localStorage
window.addEventListener('load', () => {
  const theme = localStorage.getItem('theme') || 'dark';
  document.body.className = `theme-${theme}`;
});

// Auth
function restoreSession() {
  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const role = localStorage.getItem('role');
  if (token && username) {
    currentToken = token;
    currentUser = username;
    currentUserRole = role || 'user';
    updateAuthUI();
  }
}

function updateAuthUI() {
  const btn = document.querySelector('button.secondary-button');
  if (btn && btn.textContent === 'Вход') {
    btn.textContent = currentUser;
    btn.onclick = () => showProfileModal();
  }
}

function showAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) {
    modal.classList.remove('hidden');
  }
}

function hideAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) {
    modal.classList.add('hidden');
  }
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.reset();
  }
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.reset();
  }
}

function switchAuthTab(tab) {
  const tabButtons = document.querySelectorAll('#authModal .tab-button');
  const tabPanels = document.querySelectorAll('#authModal .tab-panel');
  
  tabButtons.forEach(b => b.classList.remove('active'));
  tabPanels.forEach(p => p.classList.remove('active'));
  
  if (event && event.target) {
    event.target.classList.add('active');
  }
  
  const tabPanel = document.getElementById(tab + 'Tab');
  if (tabPanel) {
    tabPanel.classList.add('active');
  }
}

function switchProfileTab(tab) {
  const tabButtons = document.querySelectorAll('#profileModal .tab-button');
  const tabPanels = document.querySelectorAll('#profileModal .tab-panel');
  
  tabButtons.forEach(b => b.classList.remove('active'));
  tabPanels.forEach(p => p.classList.remove('active'));
  
  if (event && event.target) {
    event.target.classList.add('active');
  }
  
  const tabPanel = document.getElementById(tab + 'Tab');
  if (tabPanel) {
    tabPanel.classList.add('active');
  }
  
  if (tab === 'favorites') {
    loadFavorites();
  }
}

function showProfileModal() {
  const usernameEl = document.getElementById('profileUsername');
  if (usernameEl) {
    usernameEl.textContent = currentUser || 'Пользователь';
  }
  
  const roleEl = document.getElementById('profileRole');
  if (roleEl) {
    roleEl.textContent = currentUserRole === 'admin' ? 'Администратор' : 'Зритель';
  }
  
  const adminTab = document.getElementById('adminTabButton');
  if (adminTab) {
    adminTab.style.display = currentUserRole === 'admin' ? 'block' : 'none';
  }
  
  const modal = document.getElementById('profileModal');
  if (modal) {
    modal.classList.remove('hidden');
  }
}

function hideProfileModal() {
  const modal = document.getElementById('profileModal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

// AUTH LOGIN
async function handleLogin(e) {
  e.preventDefault();
  const usernameEl = document.getElementById('loginUsername');
  const passwordEl = document.getElementById('loginPassword');
  
  const username = usernameEl ? usernameEl.value.trim() : '';
  const password = passwordEl ? passwordEl.value.trim() : '';
  
  if (!username || !password) {
    alert('Заполните логин и пароль');
    return;
  }
  
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('username', username);
      localStorage.setItem('role', data.role || 'user');
      currentToken = data.access_token;
      currentUser = username;
      currentUserRole = data.role || 'user';
      hideAuthModal();
      updateAuthUI();
      loadMovies();
      loadFavoritesSet();
    } else {
      const error = await response.json();
      alert('Неверные данные: ' + (error.detail || 'Ошибка входа'));
    }
  } catch (err) {
    console.error('Login error:', err);
    alert('Ошибка сети: ' + err.message);
  }
}

async function quickLogin(username) {
  const password = '1234';
  
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('username', username);
      localStorage.setItem('role', data.role || 'user');
      currentToken = data.access_token;
      currentUser = username;
      currentUserRole = data.role || 'user';
      hideAuthModal();
      updateAuthUI();
      loadMovies();
      loadFavoritesSet();
    } else {
      alert('Ошибка при входе');
    }
  } catch (err) {
    console.error('Quick login error:', err);
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const usernameEl = document.getElementById('registerUsername');
  const passwordEl = document.getElementById('registerPassword');
  
  const username = usernameEl ? usernameEl.value.trim() : '';
  const password = passwordEl ? passwordEl.value.trim() : '';
  
  if (!username || !password) {
    alert('Заполните все поля');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email: '', password })
    });
    
    if (response.ok) {
      alert('Регистрация успешна! Нажмите "Войти" для входа.');
      const registerForm = document.getElementById('registerForm');
      if (registerForm) {
        registerForm.reset();
      }
      switchAuthTab('login');
    } else {
      const error = await response.json();
      alert('Ошибка: ' + (error.detail || 'Не удалось регистрироваться'));
    }
  } catch (err) {
    console.error('Register error:', err);
    alert('Ошибка регистрации: ' + err.message);
  }
}

function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('role');
  currentToken = null;
  currentUser = null;
  currentUserRole = null;
  favoritesSet.clear();
  location.reload();
}

// Movies
async function loadMovies() {
  try {
    const response = await fetch(`${API_URL}/movies`);
    if (response.ok) {
      allMovies = await response.json();
      renderMovies();
      if (currentToken) loadFavoritesSet();
    }
  } catch (err) {
    console.error('Error loading movies:', err);
  }
}

async function loadFavoritesSet() {
  if (!currentToken) {
    favoritesSet.clear();
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/favorites`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    
    if (response.ok) {
      const favorites = await response.json();
      favoritesSet = new Set(favorites.map(f => f.id));
      updateFavButtonStates();
    }
  } catch (err) {
    console.error('Error loading favorites:', err);
  }
}

function updateFavButtonStates() {
  document.querySelectorAll('.fav-button').forEach(btn => {
    const movieId = parseInt(btn.dataset.movieId);
    if (favoritesSet.has(movieId)) {
      btn.textContent = '★';
      btn.classList.add('active');
    } else {
      btn.textContent = '☆';
      btn.classList.remove('active');
    }
  });
}

function filterByPick(pick) {
  currentFilter.pick = pick;
  
  // Update pill buttons
  document.querySelectorAll('.top-bar-center .pill-button').forEach(btn => btn.classList.remove('active'));
  const activeBtn = Array.from(document.querySelectorAll('.top-bar-center .pill-button')).find(btn => btn.getAttribute('data-pick') === pick);
  if (activeBtn) {
    activeBtn.classList.add('active');
  }
  
  renderMovies();
}

function filterByRating(rating) {
  currentFilter.rating = rating;
  
  // Update chip buttons
  document.querySelectorAll('.rating-filter .chip-button').forEach(btn => btn.classList.remove('active'));
  const activeBtn = Array.from(document.querySelectorAll('.rating-filter .chip-button')).find(btn => btn.getAttribute('data-rating') === rating.toString());
  if (activeBtn) {
    activeBtn.classList.add('active');
  }
  
  renderMovies();
}

function renderMovies() {
  const list = document.getElementById('moviesList');
  if (!list) return;
  
  list.innerHTML = '';
  
  let filtered = allMovies;
  
  // Filter by pick
  if (currentFilter.pick !== 'all') {
    filtered = filtered.filter(m => m.picks && m.picks.includes(currentFilter.pick));
  }
  
  // Filter by rating
  if (currentFilter.rating > 0) {
    filtered = filtered.filter(m => m.rating >= currentFilter.rating);
  }
  
  filtered.forEach(movie => {
    const li = document.createElement('li');
    li.className = 'movie-card';
    li.dataset.id = movie.id;
    li.onclick = () => showMovieDetails(movie);
    
    const picksHtml = (movie.picks || []).map(p => 
      `<span class="movie-pick-chip">${p}</span>`
    ).join('');
    
    li.innerHTML = `
      <div class="movie-poster-wrapper">
        <img src="${movie.poster_url || 'https://via.placeholder.com/200x300'}" class="movie-poster" alt="${movie.title}" onerror="this.src='https://via.placeholder.com/200x300/333/666?text=No+Poster'">
      </div>
      <div class="movie-card-body">
        <div class="movie-card-header">
          <h3 class="movie-title">${movie.title}</h3>
          <button class="fav-button" data-movie-id="${movie.id}" onclick="event.stopPropagation(); toggleFavorite(${movie.id}, this)" title="Добавить в избранное">☆</button>
        </div>
        <div class="movie-meta">
          <span class="badge-rating">★ ${movie.rating}</span>
          <span class="badge-genre">${movie.genre || 'N/A'}</span>
        </div>
        <div class="movie-card-footer">
          <span>${movie.year}</span>
          <div class="movie-picks">${picksHtml}</div>
        </div>
      </div>
    `;
    
    list.appendChild(li);
  });
  
  updateFavButtonStates();
}

async function showMovieDetails(movie) {
  selectedMovieId = movie.id;
  const details = document.getElementById('movieDetails');
  if (!details) return;
  
  details.innerHTML = `
    <div class="details-scroll">
      <div class="details-header-top">
        <div class="details-poster-wrapper">
          <img src="${movie.poster_url || 'https://via.placeholder.com/90x115'}" class="details-poster" alt="${movie.title}">
        </div>
        <div class="details-header">
          <div class="details-title-row">
            <h2 class="details-title">${movie.title}</h2>
            <button class="fav-button" data-movie-id="${movie.id}" onclick="toggleFavorite(${movie.id}, this)" title="Добавить в избранное">☆</button>
          </div>
          <div class="details-meta-row">
            <span>${movie.year}</span>
            <span>•</span>
            <span>${movie.genre}</span>
            <span>•</span>
            <span class="badge-rating">★ ${movie.rating}</span>
          </div>
        </div>
      </div>
      
      <div class="details-section">
        <h4 class="details-section-title">Описание</h4>
        <p class="details-overview">${movie.overview || 'Описание отсутствует'}</p>
      </div>
      
      <div class="details-section">
        <h4 class="details-section-title">Рецензии</h4>
        <div id="reviewsList">Гружу...</div>
      </div>
      
      ${currentToken ? `
      <div class="details-section">
        <h4 class="details-section-title">Моя рецензия</h4>
        <form class="review-form">
          <div class="review-form-row">
            <textarea class="input" id="reviewText" placeholder="Ваше мнение..." rows="3" required></textarea>
          </div>
          <div class="review-form-rating-row">
            <label class="form-label">Оценка (1-10):</label>
            <input type="number" class="input review-rating-select" id="reviewRating" min="1" max="10" value="8" required>
            <button type="button" class="primary-button small" onclick="submitReview(${movie.id})">Okправить</button>
          </div>
        </form>
      </div>
      ` : ''}
    </div>
  `;
  
  details.classList.remove('empty');
  loadReviews(movie.id);
  updateFavButtonStates();
}

async function loadReviews(movieId) {
  try {
    const response = await fetch(`${API_URL}/reviews?movie_id=${movieId}`);
    if (response.ok) {
      const reviews = await response.json();
      const container = document.getElementById('reviewsList');
      if (!container) return;
      
      if (reviews.length === 0) {
        container.innerHTML = '<p style="color: var(--color-muted);">Рецензий нет</p>';
      } else {
        container.innerHTML = reviews.map(r => `
          <div class="review-item">
            <div class="review-header">
              <span class="review-author">${r.author_name}</span>
              <span class="review-rating-badge">★ ${r.rating}</span>
            </div>
            <p class="review-text">${r.text}</p>
          </div>
        `).join('');
      }
    }
  } catch (err) {
    console.error('Error loading reviews:', err);
  }
}

async function submitReview(movieId) {
  const textEl = document.getElementById('reviewText');
  const ratingEl = document.getElementById('reviewRating');
  
  const text = textEl ? textEl.value.trim() : '';
  const rating = ratingEl ? parseInt(ratingEl.value) : 0;
  
  if (!text || !rating) {
    alert('Заполните текст и оценку');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/reviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`
      },
      body: JSON.stringify({ movie_id: movieId, text, rating })
    });
    
    if (response.ok) {
      if (textEl) textEl.value = '';
      if (ratingEl) ratingEl.value = '8';
      loadReviews(movieId);
      alert('Рецензия добавлена!');
    } else {
      alert('Ошибка при добавлении рецензии');
    }
  } catch (err) {
    console.error(err);
  }
}

async function toggleFavorite(movieId, btn) {
  if (!currentToken) {
    showAuthModal();
    return;
  }
  
  try {
    const isFav = favoritesSet.has(movieId);
    const method = isFav ? 'DELETE' : 'POST';
    
    const response = await fetch(`${API_URL}/favorites/${movieId}`, {
      method: method,
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    
    if (response.ok) {
      if (isFav) {
        favoritesSet.delete(movieId);
      } else {
        favoritesSet.add(movieId);
      }
      updateFavButtonStates();
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadFavorites() {
  if (!currentToken) return;
  
  try {
    const response = await fetch(`${API_URL}/favorites`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    
    if (response.ok) {
      const favorites = await response.json();
      const list = document.getElementById('favoritesList');
      if (!list) return;
      
      if (favorites.length === 0) {
        list.innerHTML = '<li style="text-align: center; color: var(--color-muted); padding: 16px;">Избранных нет</li>';
      } else {
        list.innerHTML = favorites.map(m => `
          <li class="movie-card" onclick="showMovieDetails({id: ${m.id}, title: '${m.title.replace(/'/g, "\\'")}'})" style="cursor: pointer;">
            <div class="movie-poster-wrapper">
              <img src="${m.poster_url}" class="movie-poster" alt="${m.title}">
            </div>
            <div class="movie-title">${m.title}</div>
          </li>
        `).join('');
      }
    }
  } catch (err) {
    console.error(err);
  }
}

async function handleAddMovie(e) {
  e.preventDefault();
  
  if (currentUserRole !== 'admin') {
    alert('Только администраторы могут добавлять фильмы');
    return;
  }
  
  const titleEl = document.getElementById('adminTitle');
  const yearEl = document.getElementById('adminYear');
  const genreEl = document.getElementById('adminGenre');
  const ratingEl = document.getElementById('adminRating');
  const overviewEl = document.getElementById('adminOverview');
  
  const title = titleEl ? titleEl.value.trim() : '';
  const year = yearEl ? parseInt(yearEl.value) : 0;
  const genre = genreEl ? genreEl.value.trim() : '';
  const rating = ratingEl ? parseFloat(ratingEl.value) : 0;
  const overview = overviewEl ? overviewEl.value.trim() : '';
  
  const picsCheckboxes = document.querySelectorAll('.admin-picks input[type="checkbox"]:checked');
  const picks = Array.from(picsCheckboxes).map(cb => cb.value);
  
  if (!title || !year || !genre || !rating || !overview || picks.length === 0) {
    alert('Заполните все поля и выберите подборки');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/movies`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`
      },
      body: JSON.stringify({ title, year, genre, rating, overview, picks })
    });
    
    if (response.ok) {
      alert('Фильм добавлен!');
      const form = document.getElementById('adminAddForm');
      if (form) {
        form.reset();
      }
      loadMovies();
    } else {
      const error = await response.json();
      alert('Ошибка: ' + (error.detail || 'Не удалось добавить фильм'));
    }
  } catch (err) {
    console.error(err);
    alert('Ошибка сервера');
  }
}
