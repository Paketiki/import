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
  document.getElementById('authModal').classList.remove('hidden');
}

function hideAuthModal() {
  document.getElementById('authModal').classList.add('hidden');
  document.getElementById('loginForm').reset();
  document.getElementById('registerForm').reset();
}

function switchAuthTab(tab) {
  document.querySelectorAll('#authModal .tab-button').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#authModal .tab-panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById(tab + 'Tab').classList.add('active');
}

function switchProfileTab(tab) {
  document.querySelectorAll('#profileModal .tab-button').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#profileModal .tab-panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById(tab + 'Tab').classList.add('active');
  
  if (tab === 'favorites') {
    loadFavorites();
  }
}

function showProfileModal() {
  document.getElementById('profileUsername').textContent = currentUser;
  document.getElementById('profileRole').textContent = currentUserRole === 'admin' ? 'Администратор' : 'Зритель';
  
  const adminTab = document.getElementById('adminTabButton');
  if (currentUserRole === 'admin') {
    adminTab.style.display = 'block';
  } else {
    adminTab.style.display = 'none';
  }
  
  document.getElementById('profileModal').classList.remove('hidden');
}

function hideProfileModal() {
  document.getElementById('profileModal').classList.add('hidden');
}

// AUTH LOGIN - FIX 422 ERROR
async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value.trim();
  
  if (!username || !password) {
    alert('Заполните логин и пароль');
    return;
  }
  
  try {
    // Use FormData for proper content-type
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData  // Don't set Content-Type, browser will set it
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
      alert(анат данные: ' + (error.detail || 'Ошибка входа'));
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
  const username = document.getElementById('registerUsername').value.trim();
  const email = document.getElementById('registerEmail').value.trim();
  const password = document.getElementById('registerPassword').value.trim();
  
  if (!username || !email || !password) {
    alert('Заполните все поля');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    
    if (response.ok) {
      alert('Регистрация успешна! Нажмите "Вход" для вохода.');
      document.getElementById('registerForm').reset();
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
  document.querySelectorAll('.filter-block:first-child .chip-button').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  
  // Also update top bar buttons
  document.querySelectorAll('.top-bar-center .pill-button').forEach(btn => btn.classList.remove('active'));
  event.target.parentElement?.querySelector(`[onclick="filterByPick('${pick}')"]`)?.classList.add('active') || 
  document.querySelectorAll('.top-bar-center .pill-button')[0].classList.add('active');
  
  renderMovies();
}

function filterByRating(rating) {
  currentFilter.rating = rating;
  document.querySelectorAll('.filter-block:last-child .chip-button').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  renderMovies();
}

function renderMovies() {
  const list = document.getElementById('moviesList');
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
    li.onclick = () => showMovieDetails(movie);
    
    const picksHtml = (movie.picks || []).map(p => 
      `<div class="movie-pick-chip">${p}</div>`
    ).join('');
    
    li.innerHTML = `
      <div class="movie-poster-wrapper">
        <img src="${movie.poster_url || 'https://via.placeholder.com/200x300'}" class="movie-poster" alt="${movie.title}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22300%22%3E%3Crect fill=%22%23333%22 width=%22200%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 fill=%22%23777%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3ENo Image%3C/text%3E%3C/svg%3E'">
      </div>
      <div class="movie-card-body">
        <div class="movie-card-header">
          <div class="movie-title">${movie.title}</div>
          <button class="fav-button" data-movie-id="${movie.id}" onclick="event.stopPropagation(); toggleFavorite(${movie.id}, this)" title="Добавить в избранное">☆</button>
        </div>
        <div class="movie-meta">
          <span>${movie.year}</span>
          <span class="badge-rating">⭐ ${movie.rating}</span>
          <span class="badge-genre">${movie.genre || 'N/A'}</span>
        </div>
        <div class="movie-picks">${picksHtml}</div>
      </div>
    `;
    
    list.appendChild(li);
  });
  
  updateFavButtonStates();
}

async function showMovieDetails(movie) {
  selectedMovieId = movie.id;
  const details = document.getElementById('detailsPanel');
  details.innerHTML = `
    <div class="movie-details">
      <div class="details-header-top">
        <div class="details-poster-wrapper">
          <img src="${movie.poster_url || 'https://via.placeholder.com/90x115'}" class="details-poster" alt="${movie.title}">
        </div>
        <div class="details-header">
          <div class="details-title-row">
            <div>
              <div class="details-title">${movie.title}</div>
              <div class="details-year">${movie.year}</div>
            </div>
            <button class="fav-button" data-movie-id="${movie.id}" onclick="toggleFavorite(${movie.id}, this)" title="Добавить в избранное">☆</button>
          </div>
          <div class="details-meta-row">
            <span>${movie.genre}</span>
            <span style="background: rgba(46, 204, 113, 0.16); padding: 2px 6px; border-radius: 999px; color: #7bed9f;">⭐ ${movie.rating}</span>
          </div>
        </div>
      </div>
      
      <div class="details-scroll">
        <div class="details-section-title">О фильме</div>
        <div class="details-overview">${movie.overview || 'Описание отсутствует'}</div>
        
        <div class="details-section-title" style="margin-top: 12px;">Рецензии</div>
        <div id="reviewsList">Загружаю...</div>
        
        ${currentToken ? `
          <div class="review-form">
            <div class="form-row">
              <label class="form-label">Моя рецензия</label>
              <textarea class="input" id="reviewText" placeholder="Ваше мнение..." rows="2"></textarea>
            </div>
            <div class="review-form-rating-row">
              <label class="form-label">Оценка (1-10)</label>
              <input type="number" class="input review-rating-select" id="reviewRating" min="1" max="10" placeholder="10">
            </div>
            <button class="primary-button" onclick="submitReview(${movie.id})">Отправить</button>
          </div>
        ` : ''}
      </div>
    </div>
  `;
  
  loadReviews(movie.id);
  updateFavButtonStates();
}

async function loadReviews(movieId) {
  try {
    const response = await fetch(`${API_URL}/reviews?movie_id=${movieId}`);
    if (response.ok) {
      const reviews = await response.json();
      const container = document.getElementById('reviewsList');
      
      if (reviews.length === 0) {
        container.innerHTML = '<div class="placeholder-text">Рецензий нет</div>';
      } else {
        container.innerHTML = reviews.map(r => `
          <div class="review-item">
            <div class="review-header">
              <span class="review-author">${r.author_name}</span>
              <span class="review-role">${r.author_role || 'Зритель'}</span>
              <span class="review-rating-badge">⭐ ${r.rating}</span>
            </div>
            <div class="review-text">${r.text}</div>
          </div>
        `).join('');
      }
    }
  } catch (err) {
    console.error('Error loading reviews:', err);
  }
}

async function submitReview(movieId) {
  const text = document.getElementById('reviewText').value.trim();
  const rating = parseInt(document.getElementById('reviewRating').value);
  
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
      document.getElementById('reviewText').value = '';
      document.getElementById('reviewRating').value = '';
      loadReviews(movieId);
    } else {
      alert('Ошибка при аддении рецензии');
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
      
      if (favorites.length === 0) {
        list.innerHTML = '<li style="text-align: center; color: var(--color-muted); padding: 16px;">Избранных нет</li>';
      } else {
        list.innerHTML = favorites.map(m => `
          <li class="movie-card" onclick="showMovieDetails({id: ${m.id}, title: '${m.title.replace(/'/g, "\\'")}'})">
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
  
  const title = document.getElementById('adminTitle').value.trim();
  const year = parseInt(document.getElementById('adminYear').value);
  const genre = document.getElementById('adminGenre').value.trim();
  const rating = parseFloat(document.getElementById('adminRating').value);
  const overview = document.getElementById('adminOverview').value.trim();
  const picks = Array.from(document.querySelectorAll('#addMovieForm input[name="picks"]:checked')).map(cb => cb.value);
  
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
      document.getElementById('addMovieForm').reset();
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
