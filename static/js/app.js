const API_URL = '/api/v1';
let currentUser = null;
let currentToken = null;
let allMovies = [];
let picks = [];
let selectedMovieId = null;

// Init
document.addEventListener('DOMContentLoaded', () => {
  restoreSession();
  loadMovies();
  loadPicks();
  setupTabListeners();
});

// Auth
function restoreSession() {
  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  if (token && username) {
    currentToken = token;
    currentUser = username;
    updateAuthUI();
  } else {
    showAuthButtons();
  }
}

function updateAuthUI() {
  const authArea = document.getElementById('authArea');
  if (currentUser) {
    authArea.innerHTML = `
      <span style="font-size: 13px; margin-right: 8px;">${currentUser}</span>
      <button class="secondary-button" onclick="logout()" style="padding: 6px 12px; font-size: 12px;">Выход</button>
    `;
  } else {
    showAuthButtons();
  }
}

function showAuthButtons() {
  const authArea = document.getElementById('authArea');
  authArea.innerHTML = `
    <button class="secondary-button" onclick="openLoginModal()" style="padding: 6px 10px; font-size: 12px;">Вход</button>
    <button class="primary-button" onclick="openRegisterModal()" style="padding: 6px 10px; font-size: 12px;">Регистр</button>
  `;
}

function openLoginModal() {
  document.getElementById('loginModal').classList.remove('hidden');
}

function closeLoginModal() {
  document.getElementById('loginModal').classList.add('hidden');
  document.getElementById('loginUsername').value = '';
  document.getElementById('loginPassword').value = '';
  document.getElementById('loginError').style.display = 'none';
}

function openRegisterModal() {
  document.getElementById('registerModal').classList.remove('hidden');
}

function closeRegisterModal() {
  document.getElementById('registerModal').classList.add('hidden');
  document.getElementById('regUsername').value = '';
  document.getElementById('regEmail').value = '';
  document.getElementById('regPassword').value = '';
  document.getElementById('regError').style.display = 'none';
}

function switchToLogin() {
  closeRegisterModal();
  openLoginModal();
}

function switchToRegister() {
  closeLoginModal();
  openRegisterModal();
}

async function handleLogin() {
  const username = document.getElementById('loginUsername').value;
  const password = document.getElementById('loginPassword').value;
  
  if (!username || !password) {
    showError('loginError', 'Заполните все поля');
    return;
  }
  
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
      currentToken = data.access_token;
      currentUser = username;
      closeLoginModal();
      updateAuthUI();
      loadMovies();
    } else {
      showError('loginError', 'Неверные данные');
    }
  } catch (err) {
    console.error(err);
    showError('loginError', 'Ошибка сети');
  }
}

async function handleRegister() {
  const username = document.getElementById('regUsername').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;
  
  if (!username || !email || !password) {
    showError('regError', 'Заполните все поля');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    
    if (response.ok) {
      closeRegisterModal();
      switchToLogin();
    } else {
      const data = await response.json();
      showError('regError', data.detail || 'Ошибка регистрации');
    }
  } catch (err) {
    console.error(err);
    showError('regError', 'Ошибка сети');
  }
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  currentToken = null;
  currentUser = null;
  showAuthButtons();
  selectedMovieId = null;
  document.getElementById('detailsView').style.display = 'none';
  document.getElementById('emptyState').style.display = 'block';
  document.getElementById('favoritesView').style.display = 'none';
}

function showError(elementId, message) {
  const elem = document.getElementById(elementId);
  elem.textContent = message;
  elem.style.display = 'block';
}

// Movies & Picks
async function loadMovies() {
  try {
    const response = await fetch(`${API_URL}/movies`);
    if (response.ok) {
      allMovies = await response.json();
      renderMoviesList();
    }
  } catch (err) {
    console.error('Error loading movies:', err);
  }
}

async function loadPicks() {
  const pickSet = new Set();
  allMovies.forEach(m => {
    if (m.picks && Array.isArray(m.picks)) {
      m.picks.forEach(p => pickSet.add(p));
    }
  });
  picks = Array.from(pickSet);
  renderFilters();
}

function renderFilters() {
  const container = document.getElementById('filtersContainer');
  container.innerHTML = '';
  
  // All button
  let btn = document.createElement('button');
  btn.className = 'pill-button active';
  btn.textContent = 'Все';
  btn.onclick = () => filterByPick('all', btn);
  container.appendChild(btn);
  
  // Picks buttons
  picks.forEach(pick => {
    btn = document.createElement('button');
    btn.className = 'pill-button';
    btn.textContent = pick.charAt(0).toUpperCase() + pick.slice(1);
    btn.onclick = () => filterByPick(pick, btn);
    container.appendChild(btn);
  });
}

function filterByPick(pick, btn) {
  document.querySelectorAll('#filtersContainer .pill-button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  let filtered = allMovies;
  if (pick !== 'all') {
    filtered = allMovies.filter(m => m.picks && m.picks.includes(pick));
  }
  renderMoviesList(filtered);
}

function renderMoviesList(moviesToShow = allMovies) {
  const moviesList = document.getElementById('moviesList');
  moviesList.innerHTML = '';
  
  moviesToShow.forEach(movie => {
    const li = document.createElement('li');
    li.className = 'movie-card';
    
    const picksText = (movie.picks || []).join(', ');
    
    li.innerHTML = `
      <div class="movie-poster-wrapper">
        <img src="${movie.poster_url}" alt="${movie.title}" class="movie-poster" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22300%22%3E%3Crect fill=%22%23333%22 width=%22200%22 height=%22300%22/%3E%3C/svg%3E'">
      </div>
      <div class="movie-info">
        <div>
          <div class="movie-title">${movie.title}</div>
          <div class="movie-rating">⭐ ${movie.rating}</div>
          <div class="movie-picks">${movie.year} • ${picksText}</div>
        </div>
        <button class="fav-button" onclick="toggleFavorite(${movie.id}, this)" title="Добавить в избранное">☆</button>
      </div>
    `;
    
    li.onclick = () => showMovieDetails(movie);
    moviesList.appendChild(li);
  });
  
  // Load favorites if logged in
  if (currentToken) {
    loadFavorites();
  }
}

function showMovieDetails(movie) {
  selectedMovieId = movie.id;
  const detailsView = document.getElementById('detailsView');
  const emptyState = document.getElementById('emptyState');
  const favoritesView = document.getElementById('favoritesView');
  
  document.getElementById('detailTitle').textContent = movie.title;
  document.getElementById('about').innerHTML = `
    <strong>${movie.year}</strong> • ${movie.genre}<br><br>
    ${movie.overview || 'Описание отсутствует'}
  `;
  
  // Load reviews
  loadReviews(movie.id);
  
  // Update favorites button
  checkIfFavorite(movie.id);
  
  detailsView.style.display = 'block';
  emptyState.style.display = 'none';
  favoritesView.style.display = 'none';
}

async function loadReviews(movieId) {
  try {
    const response = await fetch(`${API_URL}/reviews?movie_id=${movieId}`);
    if (response.ok) {
      const reviews = await response.json();
      const reviewsContainer = document.getElementById('reviews');
      reviewsContainer.innerHTML = '';
      
      if (reviews.length === 0) {
        reviewsContainer.innerHTML = '<p style="font-size: 12px; color: var(--color-text-soft);">Рецензий нет</p>';
      } else {
        reviews.forEach(review => {
          const div = document.createElement('div');
          div.style.cssText = 'margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 12px;';
          div.innerHTML = `
            <strong style="color: var(--color-accent);">${review.author_name}</strong><br>
            <span style="color: var(--color-text-soft);">⭐ ${review.rating}</span><br>
            <p style="margin: 4px 0 0; color: var(--color-text-soft);">${review.text}</p>
          `;
          reviewsContainer.appendChild(div);
        });
      }
    }
  } catch (err) {
    console.error('Error loading reviews:', err);
  }
}

async function toggleFavorite(movieId, btn) {
  if (!currentToken) {
    openLoginModal();
    return;
  }
  
  try {
    const isFav = btn.classList.contains('active');
    const method = isFav ? 'DELETE' : 'POST';
    
    const response = await fetch(`${API_URL}/favorites/${movieId}`, {
      method: method,
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    
    if (response.ok) {
      btn.classList.toggle('active');
      btn.textContent = isFav ? '☆' : '★';
    }
  } catch (err) {
    console.error('Error toggling favorite:', err);
  }
}

async function checkIfFavorite(movieId) {
  if (!currentToken) return;
  
  try {
    const response = await fetch(`${API_URL}/favorites/check/${movieId}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    
    if (response.ok) {
      const data = await response.json();
      const btn = document.querySelector(`button.fav-button`);
      if (btn) {
        if (data.is_favorite) {
          btn.classList.add('active');
          btn.textContent = '★';
        } else {
          btn.classList.remove('active');
          btn.textContent = '☆';
        }
      }
    }
  } catch (err) {
    console.error('Error checking favorite:', err);
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
      const favIds = new Set(favorites.map(f => f.id));
      
      document.querySelectorAll('.movie-card .fav-button').forEach(btn => {
        const movieId = parseInt(btn.parentElement.parentElement.parentElement.querySelector('.movie-title').textContent);
        // Get movieId from movie object instead
      });
      
      // Update favorite buttons
      allMovies.forEach(movie => {
        if (favIds.has(movie.id)) {
          const btn = document.querySelector(`button.fav-button[onclick*="${movie.id}"]`);
          if (btn) {
            btn.classList.add('active');
            btn.textContent = '★';
          }
        }
      });
    }
  } catch (err) {
    console.error('Error loading favorites:', err);
  }
}

function setupTabListeners() {
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tabName = e.target.dataset.tab;
      document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      e.target.classList.add('active');
      document.getElementById(tabName).classList.add('active');
    });
  });
}

// Modal close on background click
document.getElementById('loginModal').addEventListener('click', (e) => {
  if (e.target.id === 'loginModal') closeLoginModal();
});

document.getElementById('registerModal').addEventListener('click', (e) => {
  if (e.target.id === 'registerModal') closeRegisterModal();
});
