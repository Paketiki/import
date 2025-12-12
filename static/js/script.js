// static/js/script.js - Полнофункциональный скрипт с авторизацией

const API_BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    auth: {
        login: `${API_BASE_URL}/api/v1/auth/login`,
        register: `${API_BASE_URL}/api/v1/auth/register`,
        logout: `${API_BASE_URL}/api/v1/auth/logout`,
        me: `${API_BASE_URL}/api/v1/users/me`
    },
    movies: {
        list: `${API_BASE_URL}/api/v1/movies`,
        detail: (id) => `${API_BASE_URL}/api/v1/movies/${id}`,
        create: `${API_BASE_URL}/api/v1/movies`,
    },
    reviews: {
        list: `${API_BASE_URL}/api/v1/reviews`,
        create: `${API_BASE_URL}/api/v1/reviews`,
        delete: (id) => `${API_BASE_URL}/api/v1/reviews/${id}`,
    },
    favorites: {
        list: `${API_BASE_URL}/api/v1/favorites`,
        add: (id) => `${API_BASE_URL}/api/v1/favorites/${id}`,
        remove: (id) => `${API_BASE_URL}/api/v1/favorites/${id}`,
        check: (id) => `${API_BASE_URL}/api/v1/favorites/check/${id}`,
    },
    genres: `${API_BASE_URL}/api/v1/genres`,
    stats: `${API_BASE_URL}/api/v1/stats`,
    search: (q) => `${API_BASE_URL}/api/v1/search?q=${encodeURIComponent(q)}`
};

// Глобальные переменные состояния
let currentUser = null;
let currentToken = localStorage.getItem('auth_token') || null;
let allMovies = [];
let allGenres = new Set();
let allPicks = new Set();
let currentFilters = {
    pick: 'all',
    genre: 'all',
    rating: 'all',
    search: ''
};
let currentDetailsMovieId = null;
let userFavorites = new Set();
let allReviews = [];

// Инициализация при загружке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔧 DOMContentLoaded: Инициализация приложения...');
    initEventListeners();
    initTheme();
    checkAuthState();
    loadMovies();
    loadReviews();
    addGlobalStyles();
    console.log('✓ Инициализация завершена');
});

// Основные функции API
async function apiRequest(url, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };
    
    if (currentToken) {
        headers['Authorization'] = `Bearer ${currentToken}`;
    }
    
    const options = {
        method: method,
        headers: headers,
        credentials: 'include'
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        console.log(`API Request: ${method} ${url}`);
        const response = await fetch(url, options);
        
        if (response.status === 204) {
            return null;
        }
        
        const responseData = await response.json();
        
        if (!response.ok) {
            throw new Error(responseData?.detail || `HTTP ${response.status}`);
        }
        
        return responseData;
    } catch (error) {
        console.error(`API Error (${method} ${url}):`, error);
        throw error;
    }
}

// Проверка авторизации
async function checkAuthState() {
    if (currentToken) {
        try {
            const response = await apiRequest(API_ENDPOINTS.auth.me, 'GET');
            currentUser = response;
            updateAuthUI(true);
            await loadUserFavorites();
            showNotification(`Добро пожаловать, ${currentUser.username}!`, 'success');
        } catch (error) {
            console.error('Ошибка проверки авторизации:', error);
            logout();
        }
    } else {
        updateAuthUI(false);
    }
}

// Обновление UI авторизации
function updateAuthUI(isAuthenticated) {
    const authButton = document.getElementById('authButton');
    const userBadge = document.getElementById('userBadge');
    const adminPanel = document.getElementById('adminPanel');
    
    if (isAuthenticated && currentUser) {
        authButton.classList.add('hidden');
        userBadge.classList.remove('hidden');
        
        document.getElementById('userName').textContent = currentUser.username || 'Пользователь';
        const role = currentUser.is_superuser ? 'Админ' : 'Зритель';
        document.getElementById('userRole').textContent = role;
        
        if (currentUser.is_superuser) {
            adminPanel.classList.remove('hidden');
        } else {
            adminPanel.classList.add('hidden');
        }
    } else {
        authButton.classList.remove('hidden');
        userBadge.classList.add('hidden');
        adminPanel.classList.add('hidden');
        userFavorites.clear();
    }
}

// Загружение фильмов
async function loadMovies() {
    try {
        showLoading(true);
        
        const response = await apiRequest(API_ENDPOINTS.movies.list);
        
        if (response) {
            allMovies = Array.isArray(response) ? response : [];
            renderMovies(allMovies);
            updateGenresList();
            updatePicksList();
        }
    } catch (error) {
        console.error('Ошибка загружки фильмов:', error);
        showNotification('Не удалось загрузить фильмы', 'error');
    } finally {
        showLoading(false);
    }
}

// Обновление списка подборок
function updatePicksList() {
    allPicks.clear();
    allMovies.forEach(movie => {
        if (movie.picks && Array.isArray(movie.picks)) {
            movie.picks.forEach(pick => {
                allPicks.add(pick);
            });
        }
    });
    
    console.log('Available picks:', Array.from(allPicks));
}

// Загружение избранных фильмов пользователя
async function loadUserFavorites() {
    if (!currentToken || !currentUser) return;
    
    try {
        const response = await apiRequest(API_ENDPOINTS.favorites.list, 'GET');
        if (response && Array.isArray(response)) {
            userFavorites.clear();
            response.forEach(movie => {
                userFavorites.add(movie.id);
            });
            // Обновим звездочки на карочках
            updateFavoritesUI();
        }
    } catch (error) {
        console.error('Ошибка загружки избранных:', error);
    }
}

// Обновление UI избранных
function updateFavoritesUI() {
    document.querySelectorAll('.fav-button').forEach(btn => {
        const card = btn.closest('.movie-card');
        const movieId = card ? parseInt(card.dataset.id) : currentDetailsMovieId;
        if (movieId) {
            btn.classList.toggle('active', userFavorites.has(movieId));
        }
    });
}

// Загружение рецензий
async function loadReviews() {
    try {
        const response = await apiRequest(API_ENDPOINTS.reviews.list, 'GET');
        if (response && Array.isArray(response)) {
            allReviews = response;
        }
    } catch (error) {
        console.error('Ошибка загружки рецензий:', error);
    }
}

// Обновление списка жанров
function updateGenresList() {
    allGenres.clear();
    allMovies.forEach(movie => {
        if (movie.genre) {
            if (typeof movie.genre === 'string' && movie.genre.includes(',')) {
                const genres = movie.genre.split(',').map(g => g.trim());
                genres.forEach(g => allGenres.add(g));
            } else {
                allGenres.add(movie.genre);
            }
        }
    });
    
    const genreSelect = document.getElementById('genreSelect');
    if (genreSelect) {
        const currentValue = genreSelect.value;
        genreSelect.innerHTML = '<option value="all">Все жанры</option>';
        
        Array.from(allGenres).sort().forEach(genre => {
            const option = document.createElement('option');
            option.value = genre;
            option.textContent = genre;
            genreSelect.appendChild(option);
        });
        
        genreSelect.value = currentValue;
    }
}

// Отрисовка фильмов
function renderMovies(movies) {
    const moviesList = document.getElementById('moviesList');
    if (!moviesList) return;
    
    if (!movies || movies.length === 0) {
        moviesList.innerHTML = `
            <li style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--color-text-soft);">
                <p>Фильмы не найдены</p>
                <button class="primary-button" onclick="loadMovies()" style="margin-top: 10px;">
                    Загрузить фильмы
                </button>
            </li>
        `;
        return;
    }
    
    moviesList.innerHTML = '';
    
    movies.forEach(movie => {
        const isFavorite = userFavorites.has(movie.id);
        const movieCard = document.createElement('li');
        movieCard.className = 'movie-card';
        movieCard.dataset.id = movie.id;
        
        const picksHTML = movie.picks && Array.isArray(movie.picks) ? movie.picks.map(pick => 
            `<span class="movie-pick-chip">${pick}</span>`
        ).join('') : '';
        
        movieCard.innerHTML = `
            <div class="movie-poster-wrapper">
                <img src="${movie.poster_url || 'https://via.placeholder.com/300x450/333/666?text=No+Poster'}" 
                     alt="${movie.title}" 
                     class="movie-poster" 
                     loading="lazy"
                     onerror="this.src='https://via.placeholder.com/300x450/333/666?text=No+Poster'">
            </div>
            <div class="movie-card-body">
                <div class="movie-card-header">
                    <h3 class="movie-title" title="${movie.title}">${movie.title}</h3>
                    <button class="fav-button ${isFavorite ? 'active' : ''}" 
                            onclick="toggleFavorite(${movie.id}, event)"
                            title="${isFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}">
                        ★
                    </button>
                </div>
                <div class="movie-meta">
                    <span class="badge-rating">${movie.rating?.toFixed(1) || 'N/A'}</span>
                    <span class="badge-genre">${movie.genre ? movie.genre.split(',')[0] : 'Не указан'}</span>
                </div>
                <div class="movie-card-footer">
                    <span>${movie.year || 'Год не указан'}</span>
                    <div class="movie-picks">
                        ${picksHTML}
                    </div>
                </div>
            </div>
        `;
        
        movieCard.addEventListener('click', (e) => {
            if (!e.target.classList.contains('fav-button') && 
                !e.target.closest('.fav-button')) {
                showMovieDetails(movie.id);
            }
        });
        
        moviesList.appendChild(movieCard);
    });
}

// Показать детали фильма
async function showMovieDetails(movieId) {
    try {
        showLoading(true);
        currentDetailsMovieId = movieId;
        
        const movie = allMovies.find(m => m.id === movieId);
        if (!movie) {
            showNotification('Фильм не найден', 'error');
            return;
        }
        
        const detailsPanel = document.getElementById('movieDetails');
        if (!detailsPanel) return;
        
        const posterUrl = movie.poster_url || 'https://via.placeholder.com/300x450/333/666?text=No+Poster';
        const movieReviews = allReviews.filter(r => r.movie_id === movieId);
        
        detailsPanel.innerHTML = `
            <div class="details-scroll">
                <div class="details-header-top">
                    <div class="details-poster-wrapper">
                        <img src="${posterUrl}" alt="${movie.title}" class="details-poster"
                             onerror="this.src='https://via.placeholder.com/300x450/333/666?text=No+Poster'">
                    </div>
                    <div class="details-header">
                        <div class="details-title-row">
                            <h2 class="details-title">${movie.title}</h2>
                            <button class="fav-button ${userFavorites.has(movie.id) ? 'active' : ''}" 
                                    onclick="toggleFavorite(${movie.id}, event)">
                                ★
                            </button>
                        </div>
                        <div class="details-meta-row">
                            <span>${movie.year || 'Год не указан'}</span>
                            <span>•</span>
                            <span>${movie.genre || 'Жанр не указан'}</span>
                            <span>•</span>
                            <span class="badge-rating">${movie.rating?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div class="details-tags">
                            ${movie.picks && Array.isArray(movie.picks) ? movie.picks.map(pick => 
                                `<span class="movie-pick-chip">${pick}</span>`
                            ).join('') : ''}
                        </div>
                    </div>
                </div>
                
                <div class="details-section">
                    <h4 class="details-section-title">Описание</h4>
                    <p class="details-overview">${movie.overview || 'Нет описания фильма'}</p>
                </div>
                
                <div class="details-section">
                    <h4 class="details-section-title">Рецензии (${movieReviews.length})</h4>
                    <div class="reviews-list">
                        ${movieReviews.length > 0 ? movieReviews.map(review => `
                            <div class="review-item">
                                <div class="review-header">
                                    <div>
                                        <span class="review-author">${review.author_name || 'Аноним'}</span>
                                        <span class="review-rating-badge">${review.rating || 0}★</span>
                                    </div>
                                    ${(currentUser?.is_superuser || currentUser?.id === review.user_id) ? `
                                        <button class="icon-button" onclick="deleteReview(${review.id})" title="Удалить">❌</button>
                                    ` : ''}
                                </div>
                                <p class="review-text">${review.text || ''}</p>
                            </div>
                        `).join('') : '<p style="color: var(--color-text-soft);">Нет рецензий</p>'}
                    </div>
                </div>
                
                ${currentUser ? `
                <div class="details-section">
                    <h4 class="details-section-title">Добавить рецензию</h4>
                    <form id="reviewForm" class="review-form">
                        <div class="review-form-row">
                            <textarea id="reviewText" class="input" 
                                      placeholder="Ваше мнение о фильме..." 
                                      rows="3" required></textarea>
                        </div>
                        <div class="review-form-rating-row">
                            <label for="reviewRating">Оценка:</label>
                            <select id="reviewRating" class="input review-rating-select">
                                ${[1,2,3,4,5,6,7,8,9,10].map(n => 
                                    `<option value="${n}" ${n === 8 ? 'selected' : ''}>${n}</option>`
                                ).join('')}
                            </select>
                            <button type="submit" class="primary-button small">Отправить</button>
                        </div>
                    </form>
                </div>
                ` : ''}
            </div>
        `;
        
        detailsPanel.classList.remove('empty');
        
        const reviewForm = document.getElementById('reviewForm');
        if (reviewForm) {
            reviewForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await submitReview(movieId);
            });
        }
        
    } catch (error) {
        console.error('Ошибка загружки деталей фильма:', error);
        showNotification('Не удалось загрузить информацию о фильме', 'error');
    } finally {
        showLoading(false);
    }
}

// Отправить рецензию
async function submitReview(movieId) {
    try {
        const reviewText = document.getElementById('reviewText').value;
        const reviewRating = parseInt(document.getElementById('reviewRating').value);
        
        if (!reviewText.trim()) {
            showNotification('Введите текст рецензии', 'warning');
            return;
        }
        
        showLoading(true);
        
        const reviewData = {
            movie_id: movieId,
            text: reviewText,
            rating: reviewRating
        };
        
        const response = await apiRequest(API_ENDPOINTS.reviews.create, 'POST', reviewData);
        
        if (response) {
            showNotification('Рецензия отправлена!', 'success');
            document.getElementById('reviewText').value = '';
            document.getElementById('reviewRating').value = '8';
            
            // Обновляем рецензии
            allReviews.push(response);
            showMovieDetails(movieId);
        }
    } catch (error) {
        console.error('Ошибка отправки рецензии:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Удалить рецензию
async function deleteReview(reviewId) {
    if (!confirm('Вы уверены?')) return;
    
    try {
        showLoading(true);
        await apiRequest(API_ENDPOINTS.reviews.delete(reviewId), 'DELETE');
        showNotification('Рецензия удалена', 'success');
        
        // Обновляем рецензии
        allReviews = allReviews.filter(r => r.id !== reviewId);
        showMovieDetails(currentDetailsMovieId);
    } catch (error) {
        console.error('Ошибка удаления рецензии:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Переключение избранного
async function toggleFavorite(movieId, event = null) {
    if (event) event.stopPropagation();
    
    if (!currentToken || !currentUser) {
        showNotification('Войдите, чтобы добавлять в избранное', 'warning');
        document.getElementById('authButton').click();
        return;
    }
    
    try {
        const isCurrentlyFavorite = userFavorites.has(movieId);
        showLoading(true);
        
        if (isCurrentlyFavorite) {
            await apiRequest(API_ENDPOINTS.favorites.remove(movieId), 'DELETE');
            userFavorites.delete(movieId);
            showNotification('Удалено из избранного', 'info');
        } else {
            await apiRequest(API_ENDPOINTS.favorites.add(movieId), 'POST');
            userFavorites.add(movieId);
            showNotification('Добавлено в избранное', 'success');
        }
        
        updateFavoritesUI();
    } catch (error) {
        console.error('Ошибка тоггла избранного:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Добавление нового фильма (админ)
async function addNewMovie(e) {
    e.preventDefault();
    
    if (!currentUser?.is_superuser) {
        showNotification('Только администратор может добавлять фильмы', 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        const title = document.getElementById('adminTitle').value.trim();
        const year = parseInt(document.getElementById('adminYear').value);
        const rating = parseFloat(document.getElementById('adminRating').value);
        const genre = document.getElementById('adminGenre').value.trim();
        const poster = document.getElementById('adminPoster').value.trim();
        const overview = document.getElementById('adminOverview').value.trim();
        
        // Собираем выбранные подборки
        const picks = [];
        document.querySelectorAll('.admin-picks input[type="checkbox"]:checked').forEach(checkbox => {
            picks.push(checkbox.value);
        });
        
        if (!title || !year || !genre || picks.length < 2) {
            showNotification('Заполните все поля и выберите хотя бы 2 подборки', 'warning');
            showLoading(false);
            return;
        }
        
        const movieData = {
            title: title,
            year: year,
            rating: rating,
            genre: genre,
            poster_url: poster || null,
            overview: overview,
            picks: picks
        };
        
        console.log('Sending movie data:', movieData);
        
        const response = await apiRequest(API_ENDPOINTS.movies.create, 'POST', movieData);
        
        if (response) {
            showNotification('Фильм успешно добавлен!', 'success');
            document.getElementById('adminAddForm').reset();
            
            // Перезагружаем список фильмов
            await loadMovies();
            loadReviews();
        }
    } catch (error) {
        console.error('Ошибка добавления фильма:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Применение фильтров
function applyFilters() {
    let filteredMovies = [...allMovies];
    
    if (currentFilters.pick && currentFilters.pick !== 'all') {
        filteredMovies = filteredMovies.filter(movie => {
            console.log(`Filtering ${movie.title} picks:`, movie.picks, 'looking for:', currentFilters.pick);
            return movie.picks && Array.isArray(movie.picks) && movie.picks.includes(currentFilters.pick);
        });
    }
    
    if (currentFilters.genre && currentFilters.genre !== 'all') {
        filteredMovies = filteredMovies.filter(movie => 
            movie.genre && movie.genre.includes(currentFilters.genre)
        );
    }
    
    if (currentFilters.rating && currentFilters.rating !== 'all') {
        const minRating = parseFloat(currentFilters.rating);
        filteredMovies = filteredMovies.filter(movie => 
            movie.rating && movie.rating >= minRating
        );
    }
    
    if (currentFilters.search) {
        const searchLower = currentFilters.search.toLowerCase();
        filteredMovies = filteredMovies.filter(movie => 
            movie.title && movie.title.toLowerCase().includes(searchLower)
        );
    }
    
    console.log('Filtered movies:', filteredMovies.length, 'from', allMovies.length);
    renderMovies(filteredMovies);
}

// Вход
async function login(username, password) {
    try {
        if (!username || !password) {
            showError('loginError', 'Введите логин и пароль');
            return;
        }
        
        showLoading(true);
        
        const response = await apiRequest(API_ENDPOINTS.auth.login, 'POST', {
            username: username.trim(),
            password: password
        });
        
        if (response && response.access_token) {
            currentToken = response.access_token;
            localStorage.setItem('auth_token', currentToken);
            
            // Проверяем авторизацию
            await checkAuthState();
            
            document.getElementById('authModal').classList.add('hidden');
            document.getElementById('loginForm').reset();
            hideError('loginError');
        }
    } catch (error) {
        console.error('Ошибка входа:', error);
        showError('loginError', error.message || 'Неверный логин или пароль');
    } finally {
        showLoading(false);
    }
}

// Регистрация
async function register(username, password) {
    try {
        if (!username || !password) {
            showError('registerError', 'Введите логин и пароль');
            return;
        }
        
        if (password.length < 4) {
            showError('registerError', 'Пароль должен содержать минимум 4 символа');
            return;
        }
        
        const confirmPassword = document.getElementById('registerPasswordConfirm').value;
        if (password !== confirmPassword) {
            showError('registerError', 'Пароли не совпадают');
            return;
        }
        
        showLoading(true);
        
        const response = await apiRequest(API_ENDPOINTS.auth.register, 'POST', {
            username: username.trim(),
            password: password,
            email: ""
        });
        
        if (response) {
            showNotification('Регистрация успешна! Входим...', 'success');
            
            setTimeout(() => {
                login(username, password);
            }, 1000);
            
            document.getElementById('registerForm').reset();
            hideError('registerError');
        }
    } catch (error) {
        console.error('Ошибка регистрации:', error);
        showError('registerError', error.message || 'Ошибка регистрации');
    } finally {
        showLoading(false);
    }
}

// Выход
async function logout() {
    try {
        if (currentToken) {
            await apiRequest(API_ENDPOINTS.auth.logout, 'POST');
        }
    } catch (error) {
        console.error('Ошибка выхода:', error);
    } finally {
        currentToken = null;
        currentUser = null;
        localStorage.removeItem('auth_token');
        userFavorites.clear();
        
        updateAuthUI(false);
        
        const detailsPanel = document.getElementById('movieDetails');
        if (detailsPanel) {
            detailsPanel.innerHTML = '<p class="placeholder-text">Выберите фильм, чтобы посмотреть рецензию.</p>';
            detailsPanel.classList.add('empty');
        }
        
        showNotification('Вы вышли из системы', 'info');
    }
}

// ===== ИНИЦИАЛИЗАЦИЯ EVENT LISTENERS =====
function initEventListeners() {
    console.log('🎯 Инициализация event listeners...');
    
    // === Кнопка входа (ГЛАВНАЯ) ===
    const authButton = document.getElementById('authButton');
    if (authButton) {
        console.log('✓ Найдена кнопка #authButton');
        authButton.addEventListener('click', (e) => {
            console.log('⚡ Клик на кнопку входа');
            e.preventDefault();
            showAuthModal();
        });
    } else {
        console.warn('❌ Кнопка #authButton НЕ найдена в DOM!');
    }

    // === Модальное окно авторизации ===
    const authModal = document.getElementById('authModal');
    const closeAuthModal = document.getElementById('closeAuthModal');
    
    if (closeAuthModal) {
        console.log('✓ Найдена кнопка закрытия модали #closeAuthModal');
        closeAuthModal.addEventListener('click', (e) => {
            e.preventDefault();
            authModal.classList.add('hidden');
        });
    }
    
    if (authModal) {
        console.log('✓ Найдена модаль авторизации #authModal');
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal || e.target.classList.contains('modal-backdrop')) {
                authModal.classList.add('hidden');
            }
        });
    }

    // === Табы в модалке ===
    document.querySelectorAll('.tab-button').forEach((tab, idx) => {
        console.log(`✓ Найдена вкладка ${idx + 1}: data-tab="${tab.dataset.tab}"`);
        tab.addEventListener('click', (e) => {
            console.log(`⚡ Переключение на вкладку: ${tab.dataset.tab}`);
            e.stopPropagation();
            const tabName = tab.dataset.tab;
            switchAuthTab(tabName);
        });
    });

    // === Форма входа ===
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('✓ Найдена форма входа #loginForm');
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('⚡ Submit формы входа');
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            login(username, password);
        });
    } else {
        console.warn('❌ Форма входа #loginForm НЕ найдена');
    }

    // === Форма регистрации ===
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        console.log('✓ Найдена форма регистрации #registerForm');
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('⚡ Submit формы регистрации');
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;
            register(username, password);
        });
    } else {
        console.warn('❌ Форма регистрации #registerForm НЕ найдена');
    }

    // === Кнопка выхода ===
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        console.log('✓ Найдена кнопка выхода #logoutButton');
        logoutButton.addEventListener('click', (e) => {
            console.log('⚡ Клик на кнопку выхода');
            e.preventDefault();
            logout();
        });
    }

    // === Фильтры подборок (pills) ===
    document.querySelectorAll('.pill-button[data-pick]').forEach((btn, idx) => {
        console.log(`✓ Найдена кнопка подборки ${idx + 1}: data-pick="${btn.dataset.pick}"`);
        btn.addEventListener('click', (e) => {
            console.log(`⚡ Фильтр подборки: ${btn.dataset.pick}`);
            e.stopPropagation();
            document.querySelectorAll('.pill-button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilters.pick = btn.dataset.pick;
            applyFilters();
        });
    });

    // === Фильтры оценок (chips) ===
    document.querySelectorAll('.chip-button[data-rating]').forEach((btn, idx) => {
        console.log(`✓ Найдена кнопка оценки ${idx + 1}: data-rating="${btn.dataset.rating}"`);
        btn.addEventListener('click', (e) => {
            console.log(`⚡ Фильтр оценки: ${btn.dataset.rating}`);
            e.stopPropagation();
            document.querySelectorAll('.chip-button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilters.rating = btn.dataset.rating;
            applyFilters();
        });
    });

    // === Поиск ===
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        console.log('✓ Найдено поле поиска #searchInput');
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentFilters.search = e.target.value.trim();
                console.log(`⚡ Поиск: "${currentFilters.search}"`);
                applyFilters();
            }, 300);
        });
        
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                currentFilters.search = '';
                applyFilters();
            }
        });
    }

    // === Выбор жанра ===
    const genreSelect = document.getElementById('genreSelect');
    if (genreSelect) {
        console.log('✓ Найдено поле жанра #genreSelect');
        genreSelect.addEventListener('change', (e) => {
            currentFilters.genre = e.target.value;
            console.log(`⚡ Жанр: ${e.target.value}`);
            applyFilters();
        });
    }

    // === Переключение темы ===
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        console.log('✓ Найдена кнопка темы #themeToggle');
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('⚡ Переключение темы');
            toggleTheme();
        });
    }

    // === Форма добавления фильма (админ) ===
    const adminAddForm = document.getElementById('adminAddForm');
    if (adminAddForm) {
        console.log('✓ Найдена форма добавления фильма #adminAddForm');
        adminAddForm.addEventListener('submit', addNewMovie);
    }

    // === Профиль пользователя ===
    const userBadge = document.getElementById('userBadge');
    if (userBadge) {
        console.log('✓ Найден badge пользователя #userBadge');
        userBadge.addEventListener('click', (e) => {
            if (!e.target.classList.contains('icon-button')) {
                console.log('⚡ Открытие профиля');
                showProfileModal();
            }
        });
    }
    
    // === Модаль профиля ===
    const profileModal = document.getElementById('profileModal');
    const closeProfileModal = document.getElementById('closeProfileModal');
    
    if (closeProfileModal) {
        console.log('✓ Найдена кнопка закрытия профиля #closeProfileModal');
        closeProfileModal.addEventListener('click', () => {
            profileModal.classList.add('hidden');
        });
    }
    
    if (profileModal) {
        console.log('✓ Найдена модаль профиля #profileModal');
        profileModal.addEventListener('click', (e) => {
            if (e.target === profileModal || e.target.classList.contains('modal-backdrop')) {
                profileModal.classList.add('hidden');
            }
        });
    }
    
    console.log('✅ Event listeners инициализированы успешно');
}

function showAuthModal() {
    console.log('📄 showAuthModal(): открытие модали авторизации');
    document.getElementById('authModal').classList.remove('hidden');
    switchAuthTab('login');
}

function switchAuthTab(tabName) {
    console.log(`📋 switchAuthTab("${tabName}"): переключение на вкладку`);
    // Переключение активных табов
    document.querySelectorAll('.tab-button').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    // Переключение активных панелей
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.toggle('active', panel.getAttribute('data-panel') === tabName);
    });
    
    hideError('loginError');
    hideError('registerError');
}

function showProfileModal() {
    if (!currentUser) return;
    
    const modal = document.getElementById('profileModal');
    const content = document.getElementById('profileContent');
    
    const favoriteMovies = allMovies.filter(movie => userFavorites.has(movie.id));
    
    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h3 style="margin-bottom: 10px; color: var(--color-text);">Профиль пользователя</h3>
            <div style="background: var(--color-bg-soft); padding: 15px; border-radius: var(--radius-md); border: 1px solid var(--color-border);">
                <p><strong>Имя пользователя:</strong> ${currentUser.username || 'Не указано'}</p>
                <p><strong>Email:</strong> ${currentUser.email || 'Не указан'}</p>
                <p><strong>Избранных фильмов:</strong> ${userFavorites.size}</p>
            </div>
        </div>
        
        <div>
            <h3 style="margin-bottom: 10px; color: var(--color-text);">Избранные фильмы</h3>
            ${favoriteMovies.length > 0 ? 
                `<div style="max-height: 400px; overflow-y: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">
                    ${favoriteMovies.map(movie => `
                        <div class="movie-card" style="cursor: pointer; margin: 0;" 
                             onclick="showMovieDetails(${movie.id}); document.getElementById('profileModal').classList.add('hidden')">
                            <div style="position: relative;">
                                <img src="${movie.poster_url || 'https://via.placeholder.com/200x300/333/666?text=Poster'}" 
                                     alt="${movie.title}" 
                                     style="width: 100%; height: 150px; object-fit: cover; border-radius: var(--radius-md);"
                                     onerror="this.src='https://via.placeholder.com/200x300/333/666?text=Poster'">
                                <button class="fav-button active" 
                                        onclick="toggleFavorite(${movie.id}, event)"
                                        style="position: absolute; top: 5px; right: 5px; z-index: 10;">
                                    ★
                                </button>
                            </div>
                            <div style="padding: 10px;">
                                <strong style="display: block; font-size: 13px;">${movie.title}</strong>
                                <small style="color: var(--color-text-soft);">${movie.year || ''} • ${movie.rating?.toFixed(1) || 'N/A'}</small>
                            </div>
                        </div>
                    `).join('')}
                </div>` : 
                `<div style="text-align: center; padding: 40px; color: var(--color-text-soft);">
                    <p>У вас пока нет избранных фильмов</p>
                    <p><small>Нажимайте на звёздочку ★ на карточках фильмов, чтобы добавить их в избранное</small></p>
                </div>`
            }
        </div>
    `;
    
    modal.classList.remove('hidden');
}

function toggleTheme() {
    const body = document.body;
    const isLight = body.classList.contains('theme-light');
    
    body.classList.toggle('theme-light', !isLight);
    body.classList.toggle('theme-dark', isLight);
    
    const theme = isLight ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const body = document.body;
    
    body.classList.remove('theme-light', 'theme-dark');
    body.classList.add(`theme-${savedTheme}`);
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.remove('hidden');
    }
}

function hideError(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = '';
        element.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    document.querySelectorAll('.notification').forEach(n => {
        if (n.parentNode) n.parentNode.removeChild(n);
    });
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 16px;
        border-radius: 8px;
        background: ${type === 'error' ? '#ff4d4f' : type === 'success' ? '#52c41a' : type === 'warning' ? '#faad14' : '#1890ff'};
        color: white;
        z-index: 9999;
        animation: fadeIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 300px;
        word-break: break-word;
        font-size: 14px;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function showLoading(show) {
    const existingLoader = document.getElementById('global-loader');
    
    if (show) {
        if (existingLoader) return;
        
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9998;
        `;
        loader.innerHTML = `
            <div style="
                background: var(--color-bg-soft);
                padding: 20px;
                border-radius: var(--radius-md);
                border: 1px solid var(--color-border);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    border: 3px solid var(--color-border);
                    border-top-color: var(--color-accent);
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                "></div>
                <span style="color: var(--color-text-soft); font-size: 14px;">Загружа...</span>
            </div>
        `;
        document.body.appendChild(loader);
    } else {
        if (existingLoader) {
            existingLoader.remove();
        }
    }
}

function addGlobalStyles() {
    if (!document.querySelector('#global-styles')) {
        const style = document.createElement('style');
        style.id = 'global-styles';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: var(--color-bg);
            }
            ::-webkit-scrollbar-thumb {
                background: var(--color-border);
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: var(--color-text-soft);
            }
            
            .movie-card {
                animation: fadeIn 0.3s ease-out;
            }
            
            @media (max-width: 768px) {
                .main-layout {
                    grid-template-columns: 1fr;
                    gap: 10px;
                }
                
                .movies-list {
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                }
                
                .details-header-top {
                    flex-direction: column;
                }
                
                .details-poster-wrapper {
                    width: 100%;
                    max-width: 200px;
                    margin: 0 auto 15px;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.classList.contains('input')) {
        const form = e.target.closest('form');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const authModal = document.getElementById('authModal');
        const profileModal = document.getElementById('profileModal');
        
        if (!authModal.classList.contains('hidden')) {
            authModal.classList.add('hidden');
        }
        
        if (!profileModal.classList.contains('hidden')) {
            profileModal.classList.add('hidden');
        }
    }
});

// Экспортируем функции
window.toggleFavorite = toggleFavorite;
window.showMovieDetails = showMovieDetails;
window.loadMovies = loadMovies;
window.login = login;
window.logout = logout;
window.showAuthModal = showAuthModal;
window.showProfileModal = showProfileModal;
window.deleteReview = deleteReview;
window.addNewMovie = addNewMovie;
