const API_URL = '/api/v1';
let currentUser = null;
let currentToken = null;
let currentUserRole = null;
let allMovies = [];
let selectedMovieId = null;
let currentFilter = { pick: 'all', rating: 0 };

// Init
document.addEventListener('DOMContentLoaded', () => {
  restoreSession();
  loadMovies();
  setupFiltering();
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
window.addEventListener('DOMContentLoaded', () => {
  const theme = localStorage.getItem('theme') || 'dark';
  document.body.classList.add(`theme-${theme}`);
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
  const topBarRight = document.querySelector('.top-bar-right');
  topBarRight.innerHTML = `
    <button class="icon-button" id="themeToggle" onclick="toggleTheme()">
      <span class="icon-sun">☀️</span>
      <span class="icon-moon">🌙</span>
    </button>
    <button class="secondary-button" onclick="showProfileModal()" style="padding: 6px 10px; font-size: 13px;">${currentUser}</button>
  `;
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
  document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
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
  } else if (tab === 'admin') {
    loadFavoritesForAdmin();
  }
}

function showProfileModal() {
  document.getElementById('profileUsername').textContent = currentUser;
  document.getElementById('profileRole').textContent = currentUserRole === 'admin' ? 'Администратор' : 'Зритель';
  
  // Show admin tab only for admins
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

async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('loginUsername').value;
  const password = document.getElementById('loginPassword').value;
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
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
    } else {
      alert('Неверные учетные данные');
    }
  } catch (err) {
    console.error(err);
    alert('Ошибка входа');
  }
}

async function quickLogin(username) {
  const password = '1234';
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
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
    }
  } catch (err) {
    console.error(err);
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const username = document.getElementById('registerUsername').value;
  const email = document.getElementById('registerEmail').value;
  const password = document.getElementById('registerPassword').value;
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    
    if (response.ok) {
      alert('Регистрация успешна! Теперь войдите.');
      switchAuthTab('login');
      document.getElementById('registerForm').reset();
    } else {
      const data = await response.json();
      alert(data.detail || 'Ошибка регистрации');
    }
  } catch (err) {
    console.error(err);
    alert('Ошибка регистрации');
  }
}

function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('role');
  currentToken = null;
  currentUser = null;
  currentUserRole = null;
  hideProfileModal();
  location.reload();
}

// Movies
async function loadMovies() {
  try {
    const response = await fetch(`${API_URL}/movies`);
    if (response.ok) {
      allMovies = await response.json();
      renderMovies();
      if (currentToken) loadFavorites();
    }
  } catch (err) {
    console.error('Error loading movies:', err);
  }
}

function setupFiltering() {
  document.querySelectorAll('.pill-button, .chip-button').forEach(btn => {
    btn.addEventListener('click', function() {
      if (this.textContent === 'Все' || this.textContent === 'Вс') {
        currentFilter.pick = 'all';
      } else if (this.textContent === 'Хиты') {
        currentFilter.pick = 'hits';
      } else if (this.textContent === 'Новинки') {
        currentFilter.pick = 'new';
      } else if (this.textContent === 'Классика') {
        currentFilter.pick = 'classic';
      } else if (this.textContent.includes('+')) {
        currentFilter.rating = parseFloat(this.textContent);
      }
      renderMovies();
    });
  });
}

function filterByPick(pick) {
  currentFilter.pick = pick;
  document.querySelectorAll('.filter-block:first-child .chip-button').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
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
        <img src="${movie.poster_url || 'https://via.placeholder.com/200x300'}" class="movie-poster" alt="${movie.title}">
      </div>
      <div class="movie-card-body">
        <div class="movie-card-header">
          <div class="movie-title">${movie.title}</div>
          <button class="fav-button" onclick="event.stopPropagation(); toggleFavorite(${movie.id}, this)" title="Добавить в избранное">☆</button>
        </div>
        <div class="movie-meta">
          <span>${movie.year}</span>
          <span class="badge-rating">${movie.rating}</span>
          <span class="badge-genre">${movie.genre || 'N/A'}</span>
        </div>
        <div class="movie-picks">${picksHtml}</div>
      </div>
    `;
    
    list.appendChild(li);
  });
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
            <button class="fav-button" onclick="toggleFavorite(${movie.id}, this)" title="Добавить в избранное">☆</button>
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
        <div id="reviewsList">Загрузка...</div>
        
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
  checkIfFavorite(movie.id);
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
              <span class="review-rating-badge">${r.rating}</span>
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
  const text = document.getElementById('reviewText').value;
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
    const isFav = btn.textContent === '★';
    const method = isFav ? 'DELETE' : 'POST';
    
    const response = await fetch(`${API_URL}/favorites/${movieId}`, {
      method: method,
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    
    if (response.ok) {
      btn.textContent = isFav ? '☆' : '★';
      btn.classList.toggle('active');
    }
  } catch (err) {
    console.error(err);
  }
}

async function checkIfFavorite(movieId) {
  if (!currentToken) return;
  
  try {
    const favorites = await fetch(`${API_URL}/favorites`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    }).then(r => r.json());
    
    const isFav = favorites.some(f => f.id === movieId);
    const btns = document.querySelectorAll('.fav-button');
    btns.forEach(btn => {
      if (btn.offsetParent) {
        btn.textContent = isFav ? '★' : '☆';
        btn.classList.toggle('active', isFav);
      }
    });
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
        list.innerHTML = '<li style="text-align: center; color: var(--color-muted); padding: 16px;">Избранных фильмов нет</li>';
      } else {
        list.innerHTML = favorites.map(m => `
          <li class="movie-card" onclick="showMovieDetails({id: ${m.id}, title: '${m.title}', poster_url: '${m.poster_url}', year: ${m.year}, genre: '${m.genre}', rating: ${m.rating}, overview: '${(m.overview || '').replace(/'/g, "\\'")}'})">
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

async function loadFavoritesForAdmin() {
  if (!currentToken || currentUserRole !== 'admin') return;
  // Placeholder for admin features
}

async function handleAddMovie(e) {
  e.preventDefault();
  
  if (currentUserRole !== 'admin') {
    alert('Только администраторы могут добавлять фильмы');
    return;
  }
  
  const title = document.getElementById('adminTitle').value;
  const year = document.getElementById('adminYear').value;
  const genre = document.getElementById('adminGenre').value;
  const rating = document.getElementById('adminRating').value;
  const overview = document.getElementById('adminOverview').value;
  const picks = Array.from(document.querySelectorAll('input[name="picks"]:checked')).map(cb => cb.value);
  
  try {
    const response = await fetch(`${API_URL}/movies`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`
      },
      body: JSON.stringify({ title, year: parseInt(year), genre, rating: parseFloat(rating), overview, picks })
    });
    
    if (response.ok) {
      alert('Фильм добавлен!');
      document.getElementById('addMovieForm').reset();
      loadMovies();
    } else {
      alert('Ошибка при добавлении фильма');
    }
  } catch (err) {
    console.error(err);
  }
}
