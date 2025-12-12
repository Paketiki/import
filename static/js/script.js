// КиноВзор - Полный JavaScript с авторизацией и API

const API_URL = window.location.origin + '/api/v1';

// Глобальнее состояние
let currentUser = null;
let currentToken = localStorage.getItem('auth_token') || null;
let allMovies = [];
let allReviews = [];
let userFavorites = new Set();
let currentFilters = {
    pick: 'all',
    genre: 'all',
    rating: 'all',
    search: ''
};
let currentMovieId = null;

// ===== Основные API функции =====

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (currentToken) {
        options.headers['Authorization'] = `Bearer ${currentToken}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(endpoint, options);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return response.status === 204 ? null : await response.json();
    } catch (error) {
        console.error(`API Error: ${error.message}`);
        throw error;
    }
}

// ===== Авторизация =====

async function login(username, password) {
    try {
        const response = await apiCall(`${API_URL}/auth/login`, 'POST', { username, password });
        currentToken = response.access_token;
        localStorage.setItem('auth_token', currentToken);
        currentUser = response;
        updateAuthUI();
        hideModal('authModal');
        showNotification(`Добро пожаловать, ${username}!`, 'success');
        await loadUserFavorites();
        return true;
    } catch (error) {
        showError('loginError', error.message);
        return false;
    }
}

async function register(username, password, passwordConfirm) {
    if (password !== passwordConfirm) {
        showError('registerError', 'Пароли не совпадают');
        return false;
    }

    try {
        await apiCall(`${API_URL}/auth/register`, 'POST', { username, password, email: '' });
        showNotification('Регистрация успешна! Входим...', 'success');
        setTimeout(() => login(username, password), 1000);
        return true;
    } catch (error) {
        showError('registerError', error.message);
        return false;
    }
}

function logout() {
    currentToken = null;
    currentUser = null;
    localStorage.removeItem('auth_token');
    userFavorites.clear();
    updateAuthUI();
    clearMovieDetails();
    showNotification('Вы вышли из системы', 'info');
}

// ===== Фильмы =====

async function loadMovies() {
    try {
        allMovies = await apiCall(`${API_URL}/movies`);
        renderMovies(allMovies);
        updateGenres();
    } catch (error) {
        showNotification('Ошибка загружки фильмов', 'error');
    }
}

async function loadReviews() {
    try {
        allReviews = await apiCall(`${API_URL}/reviews`);
    } catch (error) {
        console.error('Ошибка загружки рецензий');
    }
}

async function loadUserFavorites() {
    if (!currentToken) return;
    try {
        const favorites = await apiCall(`${API_URL}/favorites`);
        userFavorites.clear();
        if (Array.isArray(favorites)) {
            favorites.forEach(m => userFavorites.add(m.id));
        }
        updateFavoritesUI();
    } catch (error) {
        console.error('Ошибка загружки избранных');
    }
}

// ===== UI рендеринг =====

function renderMovies(movies) {
    const list = document.getElementById('moviesList');
    if (!list) return;

    list.innerHTML = '';
    movies.forEach(movie => {
        const card = document.createElement('li');
        card.className = 'movie-card';
        card.dataset.id = movie.id;
        card.innerHTML = `
            <div class="movie-poster-wrapper">
                <img src="${movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'}" 
                     alt="${movie.title}" class="movie-poster"
                     onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
            </div>
            <div class="movie-card-body">
                <div class="movie-card-header">
                    <h3 class="movie-title">${movie.title}</h3>
                    <button class="fav-button ${userFavorites.has(movie.id) ? 'active' : ''}" 
                            onclick="toggleFavorite(${movie.id}, event)">★</button>
                </div>
                <div class="movie-meta">
                    <span class="badge-rating">${(movie.rating || 0).toFixed(1)}</span>
                    <span class="badge-genre">${movie.genre || 'N/A'}</span>
                </div>
                <div class="movie-card-footer">
                    <span>${movie.year || 'N/A'}</span>
                </div>
            </div>
        `;
        card.addEventListener('click', () => showMovieDetails(movie.id));
        list.appendChild(card);
    });
}

function updateGenres() {
    const genres = new Set();
    allMovies.forEach(m => {
        if (m.genre) genres.add(m.genre);
    });
    
    const select = document.getElementById('genreSelect');
    if (select) {
        const current = select.value;
        select.innerHTML = '<option value="all">Все жанры</option>';
        genres.forEach(g => {
            const opt = document.createElement('option');
            opt.value = g;
            opt.textContent = g;
            select.appendChild(opt);
        });
        select.value = current;
    }
}

function applyFilters() {
    let filtered = allMovies;

    if (currentFilters.pick !== 'all') {
        filtered = filtered.filter(m => m.picks && m.picks.includes(currentFilters.pick));
    }
    if (currentFilters.genre !== 'all') {
        filtered = filtered.filter(m => m.genre === currentFilters.genre);
    }
    if (currentFilters.rating !== 'all') {
        const minRating = parseFloat(currentFilters.rating);
        filtered = filtered.filter(m => (m.rating || 0) >= minRating);
    }
    if (currentFilters.search) {
        const q = currentFilters.search.toLowerCase();
        filtered = filtered.filter(m => m.title.toLowerCase().includes(q));
    }

    renderMovies(filtered);
}

function showMovieDetails(movieId) {
    currentMovieId = movieId;
    const movie = allMovies.find(m => m.id === movieId);
    if (!movie) return;

    const reviews = allReviews.filter(r => r.movie_id === movieId);
    const panel = document.getElementById('movieDetails');
    
    panel.innerHTML = `
        <div class="details-scroll">
            <div class="details-header-top">
                <div class="details-poster-wrapper">
                    <img src="${movie.poster_url}" alt="${movie.title}" class="details-poster"
                         onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
                </div>
                <div class="details-header">
                    <div class="details-title-row">
                        <h2 class="details-title">${movie.title}</h2>
                        <button class="fav-button ${userFavorites.has(movie.id) ? 'active' : ''}" 
                                onclick="toggleFavorite(${movie.id}, event)">★</button>
                    </div>
                    <div class="details-meta-row">
                        <span>${movie.year}</span> • <span>${movie.genre}</span> • <span>${(movie.rating || 0).toFixed(1)}</span>
                    </div>
                </div>
            </div>

            <div class="details-section">
                <h4 class="details-section-title">Описание</h4>
                <p class="details-overview">${movie.overview || 'Нет описания'}</p>
            </div>

            <div class="details-section">
                <h4 class="details-section-title">Рецензии (${reviews.length})</h4>
                <div class="reviews-list">
                    ${reviews.map(r => `
                        <div class="review-item">
                            <div class="review-header">
                                <span class="review-author">${r.author_name || 'Аноним'}</span>
                                <span class="review-rating-badge">${r.rating}★</span>
                            </div>
                            <p class="review-text">${r.text}</p>
                        </div>
                    `).join('')}
                </div>
            </div>

            ${currentUser ? `
            <div class="details-section">
                <h4 class="details-section-title">Добавить рецензию</h4>
                <form id="reviewForm" class="review-form">
                    <textarea id="reviewText" class="input" placeholder="Ваше мнение..." rows="3" required></textarea>
                    <div class="review-form-rating-row">
                        <select id="reviewRating" class="input" style="width: auto; min-width: 70px;">
                            ${[1,2,3,4,5,6,7,8,9,10].map(n => `<option value="${n}" ${n === 8 ? 'selected' : ''}>${n}</option>`).join('')}
                        </select>
                        <button type="submit" class="primary-button small">Отправить</button>
                    </div>
                </form>
            </div>
            ` : ''}
        </div>
    `;
    panel.classList.remove('empty');

    if (currentUser && document.getElementById('reviewForm')) {
        document.getElementById('reviewForm').addEventListener('submit', submitReview);
    }
}

function clearMovieDetails() {
    const panel = document.getElementById('movieDetails');
    panel.innerHTML = '<p class="placeholder-text">Выберите фильм, чтобы посмотреть рецензию.</p>';
    panel.classList.add('empty');
}

async function submitReview(e) {
    e.preventDefault();
    if (!currentMovieId) return;

    const text = document.getElementById('reviewText').value;
    const rating = parseInt(document.getElementById('reviewRating').value);

    try {
        await apiCall(`${API_URL}/reviews`, 'POST', {
            movie_id: currentMovieId,
            text,
            rating
        });
        showNotification('Рецензия успешно добавлена!', 'success');
        await loadReviews();
        showMovieDetails(currentMovieId);
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

async function toggleFavorite(movieId, e) {
    if (e) e.stopPropagation();
    
    if (!currentToken) {
        showNotification('Войдите, чтобы добавлять в избранное', 'warning');
        document.getElementById('authButton').click();
        return;
    }

    try {
        if (userFavorites.has(movieId)) {
            await apiCall(`${API_URL}/favorites/${movieId}`, 'DELETE');
            userFavorites.delete(movieId);
            showNotification('Удалено из избранного', 'info');
        } else {
            await apiCall(`${API_URL}/favorites/${movieId}`, 'POST');
            userFavorites.add(movieId);
            showNotification('Добавлено в избранное', 'success');
        }
        updateFavoritesUI();
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

function updateFavoritesUI() {
    document.querySelectorAll('.fav-button').forEach(btn => {
        const card = btn.closest('.movie-card');
        const id = card ? parseInt(card.dataset.id) : currentMovieId;
        if (id) btn.classList.toggle('active', userFavorites.has(id));
    });
}

async function addNewMovie(e) {
    e.preventDefault();
    if (!currentUser?.is_superuser) {
        showNotification('Только админ может добавлять фильмы', 'error');
        return;
    }

    try {
        const picks = Array.from(document.querySelectorAll('.admin-picks input:checked')).map(cb => cb.value);
        
        await apiCall(`${API_URL}/movies`, 'POST', {
            title: document.getElementById('adminTitle').value,
            year: parseInt(document.getElementById('adminYear').value),
            rating: parseFloat(document.getElementById('adminRating').value),
            genre: document.getElementById('adminGenre').value,
            poster_url: document.getElementById('adminPoster').value,
            overview: document.getElementById('adminOverview').value,
            picks
        });
        showNotification('Фильм добавлен!', 'success');
        document.getElementById('adminAddForm').reset();
        await loadMovies();
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

// ===== UI работа =====

function updateAuthUI() {
    const authBtn = document.getElementById('authButton');
    const badge = document.getElementById('userBadge');
    const admin = document.getElementById('adminPanel');

    if (currentUser) {
        authBtn.classList.add('hidden');
        badge.classList.remove('hidden');
        document.getElementById('userName').textContent = currentUser.username;
        document.getElementById('userRole').textContent = currentUser.is_superuser ? 'Админ' : 'Зритель';
        if (currentUser.is_superuser) admin.classList.remove('hidden');
    } else {
        authBtn.classList.remove('hidden');
        badge.classList.add('hidden');
        admin.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    const colors = {
        success: '#52c41a',
        error: '#ff4d4f',
        warning: '#faad14',
        info: '#1890ff'
    };
    const notif = document.createElement('div');
    notif.style.cssText = `
        position: fixed; top: 20px; right: 20px; padding: 12px 16px;
        border-radius: 8px; background: ${colors[type]}; color: white;
        z-index: 9999; max-width: 300px; word-break: break-word; font-size: 14px;
    `;
    notif.textContent = message;
    document.body.appendChild(notif);
    setTimeout(() => {
        notif.style.opacity = '0';
        notif.style.transition = 'opacity 0.3s';
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

function showError(id, msg) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = msg;
        el.classList.remove('hidden');
    }
}

function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.toggle('theme-light');
    body.classList.toggle('theme-dark');
    localStorage.setItem('theme', isDark ? 'light' : 'dark');
}

function showModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('hidden');
}

function hideModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('hidden');
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(b => {
        b.classList.toggle('active', b.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-panel').forEach(p => {
        p.classList.toggle('active', p.dataset.panel === tabName);
    });
}

// ===== INIT =====

document.addEventListener('DOMContentLoaded', () => {
    // Отделяем все event listeners
    
    // Кнопки модалей
    document.getElementById('authButton')?.addEventListener('click', () => showModal('authModal'));
    document.getElementById('closeAuthModal')?.addEventListener('click', () => hideModal('authModal'));
    document.getElementById('logoutButton')?.addEventListener('click', logout);
    document.getElementById('closeProfileModal')?.addEventListener('click', () => hideModal('profileModal'));
    
    // Натик модали
    document.querySelectorAll('.modal-backdrop').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                e.target.closest('.modal').classList.add('hidden');
            }
        });
    });
    
    // Вкладки
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Формы
    document.getElementById('loginForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        login(document.getElementById('loginUsername').value, document.getElementById('loginPassword').value);
    });
    document.getElementById('registerForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        register(
            document.getElementById('registerUsername').value,
            document.getElementById('registerPassword').value,
            document.getElementById('registerPasswordConfirm').value
        );
    });
    document.getElementById('adminAddForm')?.addEventListener('submit', addNewMovie);
    
    // Фильтры
    document.querySelectorAll('.pill-button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.pill-button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilters.pick = btn.dataset.pick;
            applyFilters();
        });
    });
    
    document.querySelectorAll('.chip-button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.chip-button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilters.rating = btn.dataset.rating;
            applyFilters();
        });
    });
    
    document.getElementById('searchInput')?.addEventListener('input', (e) => {
        currentFilters.search = e.target.value.trim();
        applyFilters();
    });
    
    document.getElementById('genreSelect')?.addEventListener('change', (e) => {
        currentFilters.genre = e.target.value;
        applyFilters();
    });
    
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
    
    // Приложение
    const theme = localStorage.getItem('theme') || 'dark';
    document.body.className = `theme-${theme}`;
    
    loadMovies();
    loadReviews();
    if (currentToken) {
        // Посмотреть данные кеша
        currentUser = {
            username: localStorage.getItem('username') || 'User',
            is_superuser: localStorage.getItem('is_superuser') === 'true'
        };
        updateAuthUI();
        loadUserFavorites();
    }
});

// Экспорт для HTML
window.login = login;
window.logout = logout;
window.showModal = showModal;
window.hideModal = hideModal;
window.switchTab = switchTab;
window.toggleFavorite = toggleFavorite;
window.showMovieDetails = showMovieDetails;
window.toggleTheme = toggleTheme;
window.addNewMovie = addNewMovie;