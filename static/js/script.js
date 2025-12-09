// script.js - Полная реализация взаимодействия с API кинопортала

// ===================== КОНФИГУРАЦИЯ =====================
const API_BASE_URL = 'http://localhost:8000';
let currentUser = null;
let authToken = localStorage.getItem('token') || null;
let allMovies = [];
let favorites = [];
let currentMovieDetails = null;

// ===================== УТИЛИТЫ =====================
function showError(message) {
    console.error('Ошибка:', message);
    // Можно добавить уведомление пользователю
    alert(`Ошибка: ${message}`);
}

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        showError(`API запрос не удался: ${error.message}`);
        throw error;
    }
}

// ===================== АВТОРИЗАЦИЯ =====================
async function login(username, password) {
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });

        authToken = data.access_token;
        localStorage.setItem('token', authToken);
        
        // Получаем информацию о пользователе
        const userData = await apiRequest('/users/me');
        currentUser = userData;
        
        updateUIAfterAuth();
        closeModal('authModal');
        
        return userData;
    } catch (error) {
        const errorElement = document.getElementById('loginError');
        errorElement.textContent = 'Неверный логин или пароль';
        errorElement.classList.remove('hidden');
        throw error;
    }
}

async function register(username, password, confirmPassword) {
    if (password !== confirmPassword) {
        const errorElement = document.getElementById('registerError');
        errorElement.textContent = 'Пароли не совпадают';
        errorElement.classList.remove('hidden');
        return;
    }

    try {
        await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ 
                username, 
                password,
                email: `${username}@example.com`
            }),
        });

        // Автоматический вход после регистрации
        await login(username, password);
    } catch (error) {
        const errorElement = document.getElementById('registerError');
        errorElement.textContent = 'Ошибка регистрации. Возможно, пользователь уже существует.';
        errorElement.classList.remove('hidden');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    favorites = [];
    localStorage.removeItem('token');
    
    updateUIAfterAuth();
    loadMovies();
}

async function getCurrentUser() {
    if (!authToken) return null;
    
    try {
        const userData = await apiRequest('/users/me');
        currentUser = userData;
        return userData;
    } catch (error) {
        logout();
        return null;
    }
}

// ===================== ФИЛЬМЫ =====================
async function loadMovies(filters = {}) {
    try {
        const params = new URLSearchParams();
        if (filters.search) params.append('search', filters.search);
        if (filters.genre && filters.genre !== 'all') params.append('genre', filters.genre);
        if (filters.rating && filters.rating !== 'all') params.append('min_rating', filters.rating);
        if (filters.pick && filters.pick !== 'all') params.append('pick', filters.pick);
        params.append('skip', '0');
        params.append('limit', '100');

        const queryString = params.toString();
        const endpoint = `/movies${queryString ? `?${queryString}` : ''}`;
        
        const movies = await apiRequest(endpoint);
        allMovies = movies;
        
        renderMovies(movies);
        populateGenres(movies);
    } catch (error) {
        showError('Не удалось загрузить фильмы');
    }
}

async function loadMovieDetails(movieId) {
    try {
        const movie = await apiRequest(`/movies/${movieId}`);
        currentMovieDetails = movie;
        renderMovieDetails(movie);
        
        await loadReviews(movieId);
        
        if (currentUser) {
            await checkIfFavorite(movieId);
        }
    } catch (error) {
        showError('Не удалось загрузить детали фильма');
    }
}

async function addMovie(movieData) {
    try {
        const formattedData = {
            title: movieData.title,
            year: parseInt(movieData.year),
            genre: movieData.genre,
            rating: parseFloat(movieData.rating),
            overview: movieData.overview,
            poster_url: movieData.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster',
            picks: movieData.picks || []
        };

        if (movieData.review1) {
            formattedData.reviews = [{
                author: currentUser.username,
                role: currentUser.roles[0]?.name || 'Зритель',
                rating: parseFloat(movieData.rating),
                text: movieData.review1
            }];
            
            if (movieData.review2) {
                formattedData.reviews.push({
                    author: currentUser.username,
                    role: currentUser.roles[0]?.name || 'Зритель',
                    rating: parseFloat(movieData.rating),
                    text: movieData.review2
                });
            }
        }

        const newMovie = await apiRequest('/movies/', {
            method: 'POST',
            body: JSON.stringify(formattedData),
        });

        loadMovies();
        document.getElementById('adminAddForm').reset();
        alert(`Фильм "${newMovie.title}" успешно добавлен!`);
        
        return newMovie;
    } catch (error) {
        showError('Не удалось добавить фильм. Проверьте правильность данных.');
        throw error;
    }
}

async function deleteMovie(movieId) {
    try {
        await apiRequest(`/movies/${movieId}`, {
            method: 'DELETE',
        });
        
        alert('Фильм успешно удален');
        loadMovies();
        
        if (currentMovieDetails?.id === movieId) {
            document.getElementById('movieDetails').innerHTML = `
                <p class="placeholder-text">
                    Выберите фильм, чтобы посмотреть рецензию.
                </p>
            `;
            document.getElementById('movieDetails').className = 'movie-details empty';
        }
    } catch (error) {
        showError('Не удалось удалить фильм');
    }
}

// ===================== РЕЦЕНЗИИ =====================
async function loadReviews(movieId) {
    try {
        const reviews = await apiRequest(`/movies/${movieId}/reviews`);
        renderReviews(reviews);
    } catch (error) {
        console.error('Не удалось загрузить рецензии:', error);
    }
}

async function submitReview(movieId, reviewData) {
    try {
        await apiRequest(`/movies/${movieId}/reviews`, {
            method: 'POST',
            body: JSON.stringify(reviewData),
        });
        
        await loadReviews(movieId);
        
        const reviewForm = document.querySelector('.review-form');
        if (reviewForm) reviewForm.reset();
        
    } catch (error) {
        showError('Не удалось добавить рецензию');
        throw error;
    }
}

async function deleteReview(reviewId, movieId) {
    try {
        await apiRequest(`/movies/${movieId}/reviews/${reviewId}`, {
            method: 'DELETE',
        });
        
        await loadReviews(movieId);
    } catch (error) {
        showError('Не удалось удалить рецензию');
    }
}

// ===================== ИЗБРАННОЕ =====================
async function loadFavorites() {
    if (!currentUser) return;
    
    try {
        favorites = await apiRequest('/users/me/favorites');
        renderFavorites();
    } catch (error) {
        console.error('Не удалось загрузить избранное:', error);
    }
}

async function toggleFavorite(movieId) {
    if (!currentUser) {
        showError('Войдите в систему, чтобы добавлять фильмы в избранное');
        return;
    }

    try {
        const isCurrentlyFavorite = favorites.some(fav => fav.movie_id === movieId || fav.id === movieId);
        
        if (isCurrentlyFavorite) {
            await apiRequest(`/users/me/favorites/${movieId}`, {
                method: 'DELETE',
            });
        } else {
            await apiRequest('/users/me/favorites', {
                method: 'POST',
                body: JSON.stringify({ movie_id: movieId }),
            });
        }
        
        await loadFavorites();
        updateFavoriteButton(movieId, !isCurrentlyFavorite);
        
    } catch (error) {
        showError('Не удалось обновить избранное');
    }
}

async function checkIfFavorite(movieId) {
    if (!currentUser) return false;
    
    try {
        const favs = await apiRequest('/users/me/favorites');
        const isFav = favs.some(fav => fav.movie_id === movieId || fav.id === movieId);
        updateFavoriteButton(movieId, isFav);
        return isFav;
    } catch (error) {
        return false;
    }
}

// ===================== ПОДБОРКИ =====================
async function loadPicks() {
    try {
        const picks = await apiRequest('/picks/');
        renderPicks(picks);
        return picks;
    } catch (error) {
        console.error('Не удалось загрузить подборки:', error);
        return [];
    }
}

function renderPicks(picks) {
    // Можно использовать для динамического отображения подборок
    console.log('Подборки загружены:', picks);
}

// ===================== РЕНДЕРИНГ =====================
function renderMovies(movies) {
    const moviesList = document.getElementById('moviesList');
    if (!moviesList) return;
    
    moviesList.innerHTML = '';
    
    movies.forEach(movie => {
        const movieCard = createMovieCard(movie);
        moviesList.appendChild(movieCard);
    });
}

function createMovieCard(movie) {
    const li = document.createElement('li');
    li.className = 'movie-card';
    li.dataset.id = movie.id;
    
    const rating = movie.rating ? movie.rating.toFixed(1) : '?';
    const year = movie.year || '?';
    
    const picksHTML = movie.picks && movie.picks.length > 0 
        ? movie.picks.map(pick => 
            `<span class="movie-pick-chip">${pick.name}</span>`
          ).join('')
        : '';
    
    // Добавляем кнопку удаления для админа/модератора
    const deleteBtnHTML = (currentUser && currentUser.roles && 
        currentUser.roles.some(role => ['Администратор', 'Модератор'].includes(role.name))) 
        ? `<button class="icon-button delete-movie-btn" style="position: absolute; top: 8px; right: 8px; background: rgba(255,77,79,0.2); color: var(--color-error);" data-movie-id="${movie.id}" title="Удалить фильм">✕</button>`
        : '';
    
    li.innerHTML = `
        ${deleteBtnHTML}
        <div class="movie-poster-wrapper">
            <img src="${movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'}" 
                 alt="${movie.title}" 
                 class="movie-poster" 
                 loading="lazy">
        </div>
        <div class="movie-card-body">
            <div class="movie-card-header">
                <h3 class="movie-title" title="${movie.title}">
                    ${movie.title.length > 30 ? movie.title.substring(0, 30) + '...' : movie.title}
                </h3>
                <button class="fav-button" data-movie-id="${movie.id}" title="Добавить в избранное">
                    ★
                </button>
            </div>
            <div class="movie-meta">
                <span class="badge-rating">${rating}</span>
                <span class="badge-genre">${movie.genre || 'Не указан'}</span>
            </div>
            <div class="movie-card-footer">
                <span>${year}</span>
                <div class="movie-picks">
                    ${picksHTML}
                </div>
            </div>
        </div>
    `;
    
    li.addEventListener('click', (e) => {
        if (!e.target.closest('.fav-button') && !e.target.closest('.delete-movie-btn')) {
            loadMovieDetails(movie.id);
        }
    });
    
    const favButton = li.querySelector('.fav-button');
    favButton.addEventListener('click', async (e) => {
        e.stopPropagation();
        await toggleFavorite(movie.id);
    });
    
    const deleteBtn = li.querySelector('.delete-movie-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (confirm(`Вы уверены, что хотите удалить фильм "${movie.title}"?`)) {
                await deleteMovie(movie.id);
            }
        });
    }
    
    return li;
}

function renderMovieDetails(movie) {
    const detailsPanel = document.getElementById('movieDetails');
    if (!detailsPanel) return;
    
    detailsPanel.className = 'movie-details';
    detailsPanel.innerHTML = '';
    
    const rating = movie.rating ? movie.rating.toFixed(1) : '?';
    
    const tagsHTML = `
        <span class="badge-genre">${movie.genre || 'Не указан'}</span>
        <span>•</span>
        <span>${movie.year || '?'}</span>
        <span>•</span>
        <span class="badge-rating">${rating}</span>
    `;
    
    const picksHTML = movie.picks && movie.picks.length > 0
        ? `
        <div class="details-tags">
            ${movie.picks.map(pick => 
                `<span class="badge-genre">${pick.name}</span>`
            ).join('')}
        </div>
        `
        : '';
    
    // Кнопки управления для админа/модератора
    const adminControlsHTML = (currentUser && currentUser.roles && 
        currentUser.roles.some(role => ['Администратор', 'Модератор'].includes(role.name))) 
        ? `
        <div class="details-section">
            <h3 class="details-section-title">Управление</h3>
            <div style="display: flex; gap: 8px;">
                <button class="secondary-button" id="editMovieBtn" data-movie-id="${movie.id}">
                    Редактировать
                </button>
                <button class="primary-button" style="background: var(--color-error);" 
                        id="deleteMovieBtn" data-movie-id="${movie.id}">
                    Удалить фильм
                </button>
            </div>
        </div>
        `
        : '';
    
    const detailsHTML = `
        <div class="details-header-top">
            <div class="details-poster-wrapper">
                <img src="${movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'}" 
                     alt="${movie.title}" 
                     class="details-poster">
            </div>
            <div class="details-header">
                <div class="details-title-row">
                    <h2 class="details-title">${movie.title}</h2>
                    <button class="fav-button" data-movie-id="${movie.id}" title="Добавить в избранное">
                        ★
                    </button>
                </div>
                <div class="details-meta-row">
                    ${tagsHTML}
                </div>
                ${picksHTML}
            </div>
        </div>
        
        <div class="details-scroll">
            ${movie.overview ? `
                <div class="details-section">
                    <h3 class="details-section-title">Описание</h3>
                    <p class="details-overview">${movie.overview}</p>
                </div>
            ` : ''}
            
            <div class="details-section">
                <h3 class="details-section-title">Рецензии</h3>
                <div id="reviewsContainer">
                    <!-- Рецензии будут загружены отдельно -->
                </div>
            </div>
            
            ${currentUser ? `
                <div class="details-section">
                    <h3 class="details-section-title">Добавить рецензию</h3>
                    <form class="review-form" id="reviewForm">
                        <div class="review-form-row">
                            <textarea class="input" 
                                      placeholder="Ваша рецензия..." 
                                      rows="3" 
                                      required></textarea>
                        </div>
                        <div class="review-form-row review-form-rating-row">
                            <label>Оценка:</label>
                            <select class="input review-rating-select">
                                ${Array.from({length: 10}, (_, i) => i + 1)
                                    .map(num => `<option value="${num}" ${num === 8 ? 'selected' : ''}>${num}</option>`)
                                    .join('')}
                            </select>
                            <button type="submit" class="primary-button small">Отправить</button>
                        </div>
                    </form>
                </div>
            ` : ''}
            
            ${adminControlsHTML}
        </div>
    `;
    
    detailsPanel.innerHTML = detailsHTML;
    
    const favButton = detailsPanel.querySelector('.fav-button');
    if (favButton) {
        favButton.addEventListener('click', async () => {
            await toggleFavorite(movie.id);
        });
    }
    
    const reviewForm = detailsPanel.querySelector('#reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const textarea = reviewForm.querySelector('textarea');
            const select = reviewForm.querySelector('select');
            
            await submitReview(movie.id, {
                text: textarea.value,
                rating: parseInt(select.value),
                author: currentUser.username,
                role: currentUser.roles[0]?.name || 'Зритель'
            });
        });
    }
    
    const deleteBtn = detailsPanel.querySelector('#deleteMovieBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            if (confirm(`Вы уверены, что хотите удалить фильм "${movie.title}"?`)) {
                await deleteMovie(movie.id);
            }
        });
    }
    
    const editBtn = detailsPanel.querySelector('#editMovieBtn');
    if (editBtn) {
        editBtn.addEventListener('click', () => {
            // Здесь можно реализовать редактирование фильма
            alert('Редактирование фильма - в разработке');
        });
    }
}

function renderReviews(reviews) {
    const reviewsContainer = document.getElementById('reviewsContainer');
    if (!reviewsContainer) return;
    
    if (!reviews || reviews.length === 0) {
        reviewsContainer.innerHTML = '<p class="placeholder-text">Пока нет рецензий. Будьте первым!</p>';
        return;
    }
    
    reviewsContainer.innerHTML = reviews.map(review => `
        <div class="review-item" data-review-id="${review.id}">
            <div class="review-header">
                <span class="review-author">${review.author || 'Аноним'}</span>
                <span class="review-role">${review.role || 'Зритель'}</span>
                ${review.rating ? `
                    <span class="review-rating-badge">${review.rating.toFixed(1)}</span>
                ` : ''}
                ${(currentUser && (currentUser.username === review.author || 
                  currentUser.roles?.some(role => ['Администратор', 'Модератор'].includes(role.name)))) 
                  ? `<button class="icon-button delete-review-btn" 
                         style="margin-left: auto; background: rgba(255,77,79,0.1); color: var(--color-error); font-size: 10px;"
                         data-review-id="${review.id}"
                         title="Удалить рецензию">✕</button>`
                  : ''}
            </div>
            <p class="review-text">${review.text}</p>
        </div>
    `).join('');
    
    // Добавляем обработчики для кнопок удаления рецензий
    reviewsContainer.querySelectorAll('.delete-review-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const reviewId = btn.dataset.reviewId;
            if (confirm('Удалить эту рецензию?')) {
                await deleteReview(reviewId, currentMovieDetails.id);
            }
        });
    });
}

function renderFavorites() {
    const favoritesList = document.getElementById('favoritesList');
    if (!favoritesList) return;
    
    if (!favorites || favorites.length === 0) {
        favoritesList.innerHTML = '<p class="placeholder-text">Вы пока не добавили фильмы в избранное</p>';
        return;
    }
    
    favoritesList.innerHTML = favorites.map(fav => {
        const movie = fav.movie || fav;
        return `
            <li class="movie-card" style="flex-direction:row; align-items:center; gap:12px; position:relative;">
                <div style="width:60px; height:90px; border-radius:8px; overflow:hidden; cursor:pointer;" 
                     class="favorite-poster" data-movie-id="${movie.id}">
                    <img src="${movie.poster_url || 'https://via.placeholder.com/60x90?text=No+Poster'}" 
                         alt="${movie.title}" 
                         style="width:100%; height:100%; object-fit:cover;">
                </div>
                <div style="flex:1; cursor:pointer;" class="favorite-info" data-movie-id="${movie.id}">
                    <h4 style="margin:0 0 4px 0; font-size:14px;">${movie.title}</h4>
                    <div style="display:flex; gap:6px; align-items:center;">
                        <span class="badge-rating" style="font-size:10px;">${movie.rating?.toFixed(1) || '?'}</span>
                        <span style="font-size:11px; color:var(--color-muted);">${movie.year || '?'}</span>
                        <span style="font-size:11px; color:var(--color-muted);">${movie.genre || ''}</span>
                    </div>
                </div>
                <button class="icon-button remove-favorite-btn" 
                        data-movie-id="${movie.id}"
                        title="Удалить из избранного"
                        style="background: rgba(255,77,79,0.1); color: var(--color-error);">
                    ✕
                </button>
            </li>
        `;
    }).join('');
    
    // Добавляем обработчики
    favoritesList.querySelectorAll('.favorite-poster, .favorite-info').forEach(el => {
        el.addEventListener('click', (e) => {
            const movieId = el.dataset.movieId;
            loadMovieDetails(movieId);
            closeModal('profileModal');
        });
    });
    
    favoritesList.querySelectorAll('.remove-favorite-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const movieId = btn.dataset.movieId;
            await toggleFavorite(movieId);
        });
    });
}

function populateGenres(movies) {
    const genreSelect = document.getElementById('genreSelect');
    if (!genreSelect) return;
    
    const selectedValue = genreSelect.value;
    
    while (genreSelect.options.length > 1) {
        genreSelect.remove(1);
    }
    
    const genres = new Set();
    movies.forEach(movie => {
        if (movie.genre) {
            genres.add(movie.genre);
        }
    });
    
    Array.from(genres).sort().forEach(genre => {
        const option = document.createElement('option');
        option.value = genre;
        option.textContent = genre;
        genreSelect.appendChild(option);
    });
    
    if (selectedValue && Array.from(genres).includes(selectedValue)) {
        genreSelect.value = selectedValue;
    }
}

// ===================== ОБНОВЛЕНИЕ UI =====================
function updateUIAfterAuth() {
    const authButton = document.getElementById('authButton');
    const userBadge = document.getElementById('userBadge');
    const userName = document.getElementById('userName');
    const userRole = document.getElementById('userRole');
    const adminPanel = document.getElementById('adminPanel');
    
    if (currentUser) {
        authButton.classList.add('hidden');
        userBadge.classList.remove('hidden');
        
        userName.textContent = currentUser.username;
        userRole.textContent = currentUser.roles && currentUser.roles.length > 0 
            ? currentUser.roles[0].name 
            : 'Зритель';
        
        if (currentUser.roles && currentUser.roles.some(role => 
            role.name === 'Администратор' || role.name === 'Модератор')) {
            adminPanel.classList.remove('hidden');
        } else {
            adminPanel.classList.add('hidden');
        }
        
        loadFavorites();
    } else {
        authButton.classList.remove('hidden');
        userBadge.classList.add('hidden');
        adminPanel.classList.add('hidden');
    }
}

function updateFavoriteButton(movieId, isFavorite) {
    const favButtons = document.querySelectorAll(`.fav-button[data-movie-id="${movieId}"]`);
    favButtons.forEach(button => {
        button.classList.toggle('active', isFavorite);
        button.title = isFavorite ? 'Удалить из избранного' : 'Добавить в избранное';
    });
}

// ===================== МОДАЛЬНЫЕ ОКНА =====================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

// ===================== ФИЛЬТРАЦИЯ И ПОИСК =====================
function setupFilters() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                loadMovies({ search: e.target.value });
            }, 300);
        });
    }
    
    const genreSelect = document.getElementById('genreSelect');
    if (genreSelect) {
        genreSelect.addEventListener('change', (e) => {
            loadMovies({ genre: e.target.value });
        });
    }
    
    const ratingButtons = document.querySelectorAll('.rating-filter .chip-button');
    ratingButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            ratingButtons.forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            loadMovies({ rating: e.target.dataset.rating });
        });
    });
    
    const pickButtons = document.querySelectorAll('.top-bar-center .pill-button');
    pickButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            pickButtons.forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            loadMovies({ pick: e.target.dataset.pick });
        });
    });
}

// ===================== ИНИЦИАЛИЗАЦИЯ =====================
function initEventListeners() {
    const authButton = document.getElementById('authButton');
    if (authButton) {
        authButton.addEventListener('click', () => openModal('authModal'));
    }
    
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }
    
    const closeAuthModal = document.getElementById('closeAuthModal');
    if (closeAuthModal) {
        closeAuthModal.addEventListener('click', () => closeModal('authModal'));
    }
    
    const closeProfileModal = document.getElementById('closeProfileModal');
    if (closeProfileModal) {
        closeProfileModal.addEventListener('click', () => closeModal('profileModal'));
    }
    
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                closeModal(modal.id);
            }
        });
    });
    
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            
            const panels = document.querySelectorAll('.tab-panel');
            panels.forEach(panel => {
                panel.classList.toggle('active', panel.dataset.panel === tab);
            });
        });
    });
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            await login(username, password);
        });
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('registerPasswordConfirm').value;
            
            await register(username, password, confirmPassword);
        });
    }
    
    const adminAddForm = document.getElementById('adminAddForm');
    if (adminAddForm) {
        adminAddForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('adminTitle').value,
                year: document.getElementById('adminYear').value,
                rating: document.getElementById('adminRating').value,
                genre: document.getElementById('adminGenre').value,
                poster_url: document.getElementById('adminPoster').value,
                overview: document.getElementById('adminOverview').value,
                review1: document.getElementById('adminReview1').value,
                review2: document.getElementById('adminReview2').value,
                picks: Array.from(document.querySelectorAll('.admin-pick input:checked'))
                    .map(checkbox => checkbox.value)
            };
            
            await addMovie(formData);
        });
    }
    
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
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
        });
    }
    
    const userBadge = document.getElementById('userBadge');
    if (userBadge) {
        userBadge.addEventListener('click', async (e) => {
            if (!e.target.closest('#logoutButton')) {
                await loadFavorites();
                openModal('profileModal');
            }
        });
    }
}

async function init() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.className = `theme-${savedTheme}`;
    
    initEventListeners();
    setupFilters();
    
    if (authToken) {
        await getCurrentUser();
        updateUIAfterAuth();
    }
    
    await loadMovies();
    await loadPicks();
}

// ===================== ЗАПУСК =====================
document.addEventListener('DOMContentLoaded', init);

// Экспортируем функции для отладки
window.app = {
    login,
    logout,
    loadMovies,
    loadMovieDetails,
    toggleFavorite,
    getCurrentUser,
    currentUser: () => currentUser,
    favorites: () => favorites,
    allMovies: () => allMovies
};