// static/js/script.js - ОБНОВЛЕННЫЙ С ПРОСТЫМИ ЭНДПОИНТАМИ
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
    }
};

// Глобальные переменные состояния
let currentUser = null;
let currentToken = localStorage.getItem('auth_token') || null;
let allMovies = [];
let allGenres = new Set();
let currentFilters = {
    pick: 'all',
    genre: 'all',
    rating: 'all',
    search: ''
};
let currentDetailsMovieId = null;
let userFavorites = new Set();

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    initTheme();
    checkAuthState();
    loadMovies();
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




// Проверка состояния авторизации
async function checkAuthState() {
    if (currentToken) {
        try {
            // Для тестирования создаем фиктивного пользователя
            currentUser = {
                id: 1,
                username: localStorage.getItem('demo_username') || 'Демо-пользователь',
                email: 'demo@example.com',
                roles: [{ name: 'Зритель' }]
            };
            
            updateAuthUI(true);
            showNotification('Добро пожаловать в демо-режим!', 'info');
        } catch (error) {
            console.error('Auth check failed:', error);
            logout();
        }
    } else {
        updateAuthUI(false);
    }
}

// Обновление UI в зависимости от авторизации
function updateAuthUI(isAuthenticated) {
    const authButton = document.getElementById('authButton');
    const userBadge = document.getElementById('userBadge');
    const adminPanel = document.getElementById('adminPanel');
    
    if (isAuthenticated && currentUser) {
        authButton.classList.add('hidden');
        userBadge.classList.remove('hidden');
        
        document.getElementById('userName').textContent = currentUser.username || 'Пользователь';
        document.getElementById('userRole').textContent = 'Зритель';
        
        // Для демо показываем админ-панель
        adminPanel.classList.remove('hidden');
        
    } else {
        authButton.classList.remove('hidden');
        userBadge.classList.add('hidden');
        adminPanel.classList.add('hidden');
        userFavorites.clear();
    }
}

// Загрузка фильмов
async function loadMovies() {
    try {
        showLoading(true);
        
        const response = await apiRequest(API_ENDPOINTS.movies.list);
        
        if (response) {
            allMovies = Array.isArray(response) ? response : [];
            renderMovies(allMovies);
            updateGenresList();
        }
    } catch (error) {
        console.error('Ошибка загрузки фильмов:', error);
        showNotification('Не удалось загрузить фильмы', 'error');
        // Показываем демо-фильмы только если API недоступно
        allMovies = getDemoMovies();
        renderMovies(allMovies);
        updateGenresList();
    } finally {
        showLoading(false);
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
        
        const picksHTML = movie.picks ? movie.picks.map(pick => 
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
        
        const movie = allMovies.find(m => m.id === movieId) || getDemoMovies().find(m => m.id === movieId);
        
        const detailsPanel = document.getElementById('movieDetails');
        if (!detailsPanel) return;
        
        const posterUrl = movie.poster_url || 'https://via.placeholder.com/300x450/333/666?text=No+Poster';
        
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
                            ${movie.picks ? movie.picks.map(pick => 
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
                    <h4 class="details-section-title">Рецензии</h4>
                    <div class="reviews-list">
                        <div class="review-item">
                            <div class="review-header">
                                <span class="review-author">Кинокритик</span>
                                <span class="review-role">Эксперт</span>
                                <span class="review-rating-badge">${(movie.rating - 0.5)?.toFixed(1) || '8.0'}</span>
                            </div>
                            <p class="review-text">${movie.overview ? movie.overview.substring(0, 200) + '...' : 'Отличный фильм, рекомендую к просмотру!'}</p>
                        </div>
                        <div class="review-item">
                            <div class="review-header">
                                <span class="review-author">Зритель</span>
                                <span class="review-role">Обычный пользователь</span>
                                <span class="review-rating-badge">${(movie.rating - 1)?.toFixed(1) || '7.5'}</span>
                            </div>
                            <p class="review-text">Интересный сюжет, хорошая игра актёров. Провёл время с удовольствием.</p>
                        </div>
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
        console.error('Ошибка загрузки деталей фильма:', error);
        showNotification('Не удалось загрузить информацию о фильме', 'error');
    } finally {
        showLoading(false);
    }
}

// Отправить рецензию
async function submitReview(movieId) {
    try {
        const reviewText = document.getElementById('reviewText').value;
        const reviewRating = document.getElementById('reviewRating').value;
        
        if (!reviewText.trim()) {
            showNotification('Введите текст рецензии', 'warning');
            return;
        }
        
        showNotification('Рецензия отправлена (демо-режим)', 'success');
        document.getElementById('reviewText').value = '';
        
    } catch (error) {
        console.error('Ошибка отправки рецензии:', error);
        showNotification('Ошибка при отправке рецензии', 'error');
    }
}

// Переключение избранного
async function toggleFavorite(movieId, event = null) {
    if (event) event.stopPropagation();
    
    if (!currentToken) {
        showNotification('Войдите, чтобы добавлять в избранное', 'warning');
        document.getElementById('authButton').click();
        return;
    }
    
    const isCurrentlyFavorite = userFavorites.has(movieId);
    
    if (isCurrentlyFavorite) {
        userFavorites.delete(movieId);
        showNotification('Удалено из избранного', 'info');
    } else {
        userFavorites.add(movieId);
        showNotification('Добавлено в избранное', 'success');
    }
    
    // Обновляем кнопки
    document.querySelectorAll(`.fav-button`).forEach(btn => {
        const card = btn.closest('.movie-card');
        const details = btn.closest('.movie-details');
        
        if ((card && parseInt(card.dataset.id) === movieId) || 
            (details && currentDetailsMovieId === movieId)) {
            btn.classList.toggle('active', !isCurrentlyFavorite);
        }
    });
}

// Применение фильтров
function applyFilters() {
    let filteredMovies = [...allMovies];
    
    // Фильтр по подборкам
    if (currentFilters.pick && currentFilters.pick !== 'all') {
        filteredMovies = filteredMovies.filter(movie => 
            movie.picks && movie.picks.includes(currentFilters.pick)
        );
    }
    
    // Фильтр по жанру
    if (currentFilters.genre && currentFilters.genre !== 'all') {
        filteredMovies = filteredMovies.filter(movie => 
            movie.genre && movie.genre.includes(currentFilters.genre)
        );
    }
    
    // Фильтр по рейтингу
    if (currentFilters.rating && currentFilters.rating !== 'all') {
        const minRating = parseFloat(currentFilters.rating);
        filteredMovies = filteredMovies.filter(movie => 
            movie.rating && movie.rating >= minRating
        );
    }
    
    // Фильтр по поиску
    if (currentFilters.search) {
        const searchLower = currentFilters.search.toLowerCase();
        filteredMovies = filteredMovies.filter(movie => 
            movie.title && movie.title.toLowerCase().includes(searchLower)
        );
    }
    
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
            localStorage.setItem('demo_username', username.trim());
            
            // Создаем фиктивного пользователя
            currentUser = {
                id: 1,
                username: username.trim(),
                email: `${username.trim().toLowerCase()}@example.com`,
                roles: [{ name: 'Зритель' }]
            };
            
            updateAuthUI(true);
            loadMovies();
            
            document.getElementById('authModal').classList.add('hidden');
            showNotification(`Добро пожаловать, ${username.trim()}!`, 'success');
            
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
// script.js (частичное исправление в функции register)
async function register(username, password) {
    try {
        if (!username || !password) {
            showError('registerError', 'Пароль не должен быть именем пользователя')
            return
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
        
        // Исправляем: передаем email как пустую строку
        const response = await apiRequest(API_ENDPOINTS.auth.register, 'POST', {
            username: username.trim(),
            password: password,
            email: ""  // Явно передаем пустую строку
        });
        
        // ... остальной код ...
        
        if (response) {
            showNotification('Регистрация успешна! Входим...', 'success');
            
            // Автоматически входим после регистрации
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
        if (currentToken && currentToken !== 'temp_token_for_testing') {
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
        
        // Очищаем детали
        const detailsPanel = document.getElementById('movieDetails');
        if (detailsPanel) {
            detailsPanel.innerHTML = '<p class="placeholder-text">Выберите фильм, чтобы посмотреть рецензию.</p>';
            detailsPanel.classList.add('empty');
        }
        
        showNotification('Вы вышли из системы', 'info');
    }
}

// Добавление фильма (админ)
async function addMovie(movieData) {
    try {
        showLoading(true);
        
        // Проверяем обязательные поля
        if (!movieData.title || !movieData.year || !movieData.rating || !movieData.genre) {
            showNotification('Заполните все обязательные поля', 'warning');
            return;
        }
        
        // Преобразуем picks из чекбоксов
        const picks = [];
        document.querySelectorAll('.admin-pick input:checked').forEach(cb => {
            picks.push(cb.value);
        });
        
        const fullMovieData = {
            title: movieData.title.trim(),
            year: parseInt(movieData.year),
            rating: parseFloat(movieData.rating),
            genre: movieData.genre.trim(),
            overview: movieData.overview || '',
            poster_url: movieData.poster_url || 'https://via.placeholder.com/300x450/333/666?text=New+Movie',
            picks: picks
        };
        
        // В демо-режиме просто добавляем в локальный список
        const newMovie = {
            id: allMovies.length > 0 ? Math.max(...allMovies.map(m => m.id)) + 1 : 1,
            ...fullMovieData
        };
        
        allMovies.unshift(newMovie);
        
        showNotification('Фильм успешно добавлен! (демо-режим)', 'success');
        
        // Очищаем форму
        document.getElementById('adminAddForm').reset();
        document.querySelectorAll('.admin-pick input').forEach(cb => cb.checked = false);
        
        // Обновляем список фильмов
        setTimeout(() => {
            renderMovies(allMovies);
            updateGenresList();
        }, 500);
        
    } catch (error) {
        console.error('Ошибка добавления фильма:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Инициализация обработчиков событий
function initEventListeners() {
    // Кнопки фильтров подборок
    document.querySelectorAll('.pill-button[data-pick]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.pill-button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilters.pick = btn.dataset.pick;
            applyFilters();
        });
    });

    // Кнопки фильтров рейтинга
    document.querySelectorAll('.chip-button[data-rating]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.chip-button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilters.rating = btn.dataset.rating;
            applyFilters();
        });
    });

    // Поиск
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentFilters.search = e.target.value.trim();
                applyFilters();
            }, 300);
        });
        
        // Очистка поиска по кнопке Escape
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                currentFilters.search = '';
                applyFilters();
            }
        });
    }

    // Выбор жанра
    const genreSelect = document.getElementById('genreSelect');
    if (genreSelect) {
        genreSelect.addEventListener('change', (e) => {
            currentFilters.genre = e.target.value;
            applyFilters();
        });
    }

    // Переключение темы
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // Кнопка входа
    const authButton = document.getElementById('authButton');
    if (authButton) {
        authButton.addEventListener('click', showAuthModal);
    }

    // Кнопка выхода
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }

    // Модальное окно авторизации
    const authModal = document.getElementById('authModal');
    const closeAuthModal = document.getElementById('closeAuthModal');
    if (closeAuthModal) {
        closeAuthModal.addEventListener('click', () => {
            authModal.classList.add('hidden');
        });
    }
    if (authModal) {
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal || e.target.classList.contains('modal-backdrop')) {
                authModal.classList.add('hidden');
            }
        });
    }

    // Табы в модалке авторизации
    document.querySelectorAll('.tab-button').forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.stopPropagation();
            const tabName = tab.dataset.tab;
            switchAuthTab(tabName);
        });
    });

    // Форма логина
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            login(username, password);
        });
        
        // Автозаполнение для тестирования
        document.getElementById('loginUsername').addEventListener('focus', function() {
            if (!this.value) {
                this.value = 'user';
                document.getElementById('loginPassword').value = '1234';
            }
        });
    }

    // Форма регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;
            register(username, password);
        });
    }

    // Форма добавления фильма (админ)
    const adminForm = document.getElementById('adminAddForm');
    if (adminForm) {
        adminForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const movieData = {
                title: document.getElementById('adminTitle').value,
                year: document.getElementById('adminYear').value,
                rating: document.getElementById('adminRating').value,
                genre: document.getElementById('adminGenre').value,
                overview: document.getElementById('adminOverview').value,
                poster_url: document.getElementById('adminPoster').value
            };
            
            addMovie(movieData);
        });
        
        // Заполнение примерами для тестирования
        document.getElementById('adminTitle').addEventListener('focus', function() {
            if (!this.value) {
                const demoMovies = [
                    "Новый блокбастер 2024",
                    "История любви в Париже", 
                    "Космическая одиссея",
                    "Детективная загадка"
                ];
                this.value = demoMovies[Math.floor(Math.random() * demoMovies.length)];
                document.getElementById('adminYear').value = 2023 + Math.floor(Math.random() * 3);
                document.getElementById('adminRating').value = (6 + Math.random() * 3).toFixed(1);
                document.getElementById('adminGenre').value = ["Драма", "Комедия", "Боевик", "Фантастика"][Math.floor(Math.random() * 4)];
                document.getElementById('adminOverview').value = "Увлекательный фильм с интересным сюжетом и отличной актёрской игрой. Рекомендуется к просмотру всем любителям кино.";
                document.getElementById('adminPoster').value = "https://via.placeholder.com/300x450/333/666?text=New+Movie";
                
                // Отмечаем случайные чекбоксы
                document.querySelectorAll('.admin-pick input').forEach(cb => {
                    cb.checked = Math.random() > 0.5;
                });
            }
        });
    }

    // Профиль пользователя
    const userBadge = document.getElementById('userBadge');
    if (userBadge) {
        userBadge.addEventListener('click', (e) => {
            if (!e.target.classList.contains('icon-button')) {
                showProfileModal();
            }
        });
    }
    
    // Профиль модального окна
    const profileModal = document.getElementById('profileModal');
    const closeProfileModal = document.getElementById('closeProfileModal');
    if (closeProfileModal) {
        closeProfileModal.addEventListener('click', () => {
            profileModal.classList.add('hidden');
        });
    }
    if (profileModal) {
        profileModal.addEventListener('click', (e) => {
            if (e.target === profileModal || e.target.classList.contains('modal-backdrop')) {
                profileModal.classList.add('hidden');
            }
        });
    }
}

// Вспомогательные функции
function showAuthModal() {
    document.getElementById('authModal').classList.remove('hidden');
    switchAuthTab('login');
}

function switchAuthTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.toggle('active', panel.dataset.panel === tabName);
    });
    
    hideError('loginError');
    hideError('registerError');
}

function showProfileModal() {
    if (!currentUser) return;
    
    const modal = document.getElementById('profileModal');
    const content = document.getElementById('profileContent');
    
    // Собираем избранные фильмы
    const favoriteMovies = allMovies.filter(movie => userFavorites.has(movie.id));
    
    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h3 style="margin-bottom: 10px; color: var(--color-text);">Профиль пользователя</h3>
            <div style="background: var(--color-bg-soft); padding: 15px; border-radius: var(--radius-md); border: 1px solid var(--color-border);">
                <p><strong>Имя пользователя:</strong> ${currentUser.username || 'Не указано'}</p>
                <p><strong>Роль:</strong> ${currentUser.roles?.[0]?.name || 'Зритель'}</p>
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
    
    showNotification(`Тема изменена на ${isLight ? 'тёмную' : 'светлую'}`, 'info');
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
    // Удаляем старые уведомления
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
                <span style="color: var(--color-text-soft); font-size: 14px;">Загрузка...</span>
            </div>
        `;
        document.body.appendChild(loader);
    } else {
        if (existingLoader) {
            existingLoader.remove();
        }
    }
}

// Глобальные стили для анимаций
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
            
            /* Стили для скроллбара */
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
            
            /* Анимация появления карточек */
            .movie-card {
                animation: fadeIn 0.3s ease-out;
            }
            
            /* Адаптивность для мобильных */
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

// Добавляем обработчик для Enter в формах
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

// Добавляем обработчик для Escape для закрытия модалок
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

// Инициализация
addGlobalStyles();
initTheme();

// Экспортируем функции для использования в консоли
window.toggleFavorite = toggleFavorite;
window.showMovieDetails = showMovieDetails;
window.loadMovies = loadMovies;
window.login = login;
window.logout = logout;
window.showAuthModal = showAuthModal;
window.showProfileModal = showProfileModal;


        