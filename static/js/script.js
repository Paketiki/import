// static/js/script.js
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
        update: (id) => `${API_BASE_URL}/api/v1/movies/${id}`,
        delete: (id) => `${API_BASE_URL}/api/v1/movies/${id}`,
        search: (query) => `${API_BASE_URL}/api/v1/movies?search=${query}`
    },
    picks: {
        list: `${API_BASE_URL}/api/v1/picks`,
        get: (slug) => `${API_BASE_URL}/api/v1/picks/${slug}`
    },
    reviews: {
        list: `${API_BASE_URL}/api/v1/reviews`,
        detail: (id) => `${API_BASE_URL}/api/v1/reviews/${id}`,
        create: `${API_BASE_URL}/api/v1/reviews`,
        update: (id) => `${API_BASE_URL}/api/v1/reviews/${id}`,
        delete: (id) => `${API_BASE_URL}/api/v1/reviews/${id}`,
        byMovie: (movieId) => `${API_BASE_URL}/api/v1/reviews?movie_id=${movieId}`
    },
    users: {
        list: `${API_BASE_URL}/api/v1/users`,
        detail: (id) => `${API_BASE_URL}/api/v1/users/${id}`,
        update: (id) => `${API_BASE_URL}/api/v1/users/${id}`,
        delete: (id) => `${API_BASE_URL}/api/v1/users/${id}`,
        profile: `${API_BASE_URL}/api/v1/users/me`,
        favorites: `${API_BASE_URL}/api/v1/users/me/favorites`,
        addFavorite: `${API_BASE_URL}/api/v1/users/me/favorites`,
        removeFavorite: (movieId) => `${API_BASE_URL}/api/v1/users/me/favorites/${movieId}`,
        checkFavorite: (movieId) => `${API_BASE_URL}/api/v1/users/me/favorites/${movieId}`
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
    checkAuthState();
    
    // Загружаем данные только если авторизованы
    if (currentToken) {
        loadMovies();
    } else {
        // Показываем сообщение о необходимости авторизации
        renderMovies([]);
        document.getElementById('moviesList').innerHTML = `
            <li class="no-results" style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--color-text-soft);">
                <p>Для просмотра фильмов войдите в систему</p>
                <button class="primary-button" onclick="document.getElementById('authButton').click()">Войти</button>
            </li>
        `;
    }
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
        
        const responseData = await response.json().catch(() => null);
        
        if (!response.ok) {
            console.error(`API Error ${response.status}:`, responseData);
            
            const error = new Error(responseData?.detail || `HTTP ${response.status}`);
            error.status = response.status;
            error.response = responseData;
            throw error;
        }
        
        return responseData;
    } catch (error) {
        console.error(`API Error (${method} ${url}):`, error);
        
        if (error.status === 401) {
            showNotification('Сессия истекла. Пожалуйста, войдите снова.', 'error');
            logout();
        }
        
        throw error;
    }
}

// Проверка состояния авторизации
async function checkAuthState() {
    if (currentToken) {
        try {
            const userData = await apiRequest(API_ENDPOINTS.auth.me);
            if (userData) {
                currentUser = userData;
                updateAuthUI(true);
                loadMovies(); // Загружаем фильмы после успешной авторизации
                loadUserFavorites();
            }
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
        
        document.getElementById('userName').textContent = currentUser.username;
        
        // Определяем роль пользователя
        let roleName = 'Зритель';
        if (currentUser.roles && currentUser.roles.length > 0) {
            roleName = currentUser.roles[0].name || 'Зритель';
        } else if (currentUser.role_name) {
            roleName = currentUser.role_name;
        }
        
        document.getElementById('userRole').textContent = roleName;
        
        // Показываем админ-панель если пользователь админ
        if (roleName === 'Администратор') {
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

// Загрузка фильмов
async function loadMovies() {
    try {
        showLoading(true);
        
        // Создаем параметры запроса
        const params = new URLSearchParams({
            skip: '0',
            limit: '100'
        });
        
        if (currentFilters.genre !== 'all') {
            params.append('genre', currentFilters.genre);
        }
        
        if (currentFilters.rating !== 'all') {
            params.append('rating_min', currentFilters.rating);
        }
        
        if (currentFilters.search) {
            params.append('search', currentFilters.search);
        }
        
        if (currentFilters.pick !== 'all') {
            params.append('pick', currentFilters.pick);
        }
        
        const url = `${API_ENDPOINTS.movies.list}?${params.toString()}`;
        console.log('Loading movies from:', url);
        
        const response = await apiRequest(url);
        
        if (response) {
            allMovies = response;
            console.log(`Loaded ${allMovies.length} movies`);
            renderMovies(allMovies);
            updateGenresList();
        }
    } catch (error) {
        console.error('Ошибка загрузки фильмов:', error);
        showNotification('Ошибка загрузки фильмов: ' + (error.message || 'Неизвестная ошибка'), 'error');
        
        // Показываем тестовые данные для отладки
        if (allMovies.length === 0) {
            allMovies = [
                {
                    id: 1,
                    title: "Тестовый фильм 1",
                    year: 2023,
                    rating: 8.5,
                    genre: "Драма",
                    poster_url: "https://via.placeholder.com/300x450/FF7A1A/FFFFFF?text=Poster+1",
                    overview: "Тестовое описание фильма 1 для демонстрации",
                    picks: ["hits", "new"]
                },
                {
                    id: 2,
                    title: "Тестовый фильм 2",
                    year: 2022,
                    rating: 7.8,
                    genre: "Комедия",
                    poster_url: "https://via.placeholder.com/300x450/FF7A1A/FFFFFF?text=Poster+2",
                    overview: "Тестовое описание фильма 2 для демонстрации",
                    picks: ["classic"]
                }
            ];
            renderMovies(allMovies);
            updateGenresList();
        }
    } finally {
        showLoading(false);
    }
}

// Обновление списка жанров
function updateGenresList() {
    allGenres.clear();
    allMovies.forEach(movie => {
        if (movie.genre) {
            // Если жанры хранятся как строка с запятыми
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
        genreSelect.innerHTML = '<option value="all">Все жанры</option>';
        allGenres.forEach(genre => {
            const option = document.createElement('option');
            option.value = genre;
            option.textContent = genre;
            genreSelect.appendChild(option);
        });
        
        // Устанавливаем выбранный жанр
        genreSelect.value = currentFilters.genre;
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
    }

    // Форма регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('registerPasswordConfirm').value;
            
            if (password !== confirmPassword) {
                showError('registerError', 'Пароли не совпадают');
                return;
            }
            
            register(username, password);
        });
    }
}

// ... остальные функции (login, register, applyFilters, renderMovies и т.д.) остаются как в предыдущей версии ...

// Простая функция для отображения уведомлений
function showNotification(message, type = 'info') {
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // Можно добавить более сложную систему уведомлений
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 16px;
        border-radius: 8px;
        background: ${type === 'error' ? '#ff4d4f' : type === 'success' ? '#52c41a' : '#1890ff'};
        color: white;
        z-index: 1000;
        animation: fadeIn 0.3s ease-out;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Функция для отображения/скрытия индикатора загрузки
function showLoading(show) {
    const app = document.getElementById('app');
    if (!app) return;
    
    if (show) {
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        loader.innerHTML = '<div style="color: white; font-size: 18px;">Загрузка...</div>';
        app.appendChild(loader);
    } else {
        const loader = document.getElementById('global-loader');
        if (loader) loader.remove();
    }
}