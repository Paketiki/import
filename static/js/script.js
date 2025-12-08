 // Simple in-memory "database" of users
const USERS = [
  { username: "user", password: "1234", role: "viewer" },
  { username: "moderator", password: "1234", role: "moderator" },
];

// Movie data
let MOVIES = [];

// State
let currentUser = null;
let currentPick = "all";
let currentGenre = "all";
let currentRatingFilter = "all";
let currentSearch = "";
let selectedMovieId = null;

// API base URL - получаем из настроек приложения
const API_BASE_URL = "/api/v1";

// load favorites from localStorage (array of ids)
const FAVORITES = new Set(JSON.parse(localStorage.getItem("kinovzor-favs") || "[]"));

// Elements
const body = document.body;
const moviesListEl = document.getElementById("moviesList");
const movieDetailsEl = document.getElementById("movieDetails");
const genreSelectEl = document.getElementById("genreSelect");
const searchInputEl = document.getElementById("searchInput");
const ratingButtons = document.querySelectorAll(".chip-button[data-rating]");
const pickButtons = document.querySelectorAll(".pill-button[data-pick]");
const themeToggleBtn = document.getElementById("themeToggle");
const authButton = document.getElementById("authButton");
const userBadge = document.getElementById("userBadge");
const userNameEl = document.getElementById("userName");
const userRoleEl = document.getElementById("userRole");
const logoutButton = document.getElementById("logoutButton");
const adminPanel = document.getElementById("adminPanel");
// new profile modal elements
const profileModal = document.getElementById("profileModal");
const closeProfileModalBtn = document.getElementById("closeProfileModal");
const favoritesListEl = document.getElementById("favoritesList");
const profileContentEl = document.getElementById("profileContent");
const adminAddForm = document.getElementById("adminAddForm");
const adminTitleInput = document.getElementById("adminTitle");
const adminYearInput = document.getElementById("adminYear");
const adminRatingInput = document.getElementById("adminRating");
const adminPosterInput = document.getElementById("adminPoster");
const adminOverviewInput = document.getElementById("adminOverview");
const adminReview1Input = document.getElementById("adminReview1");
const adminReview2Input = document.getElementById("adminReview2");

// Auth modal
const authModal = document.getElementById("authModal");
const closeAuthModalBtn = document.getElementById("closeAuthModal");
const tabButtons = document.querySelectorAll(".tab-button");
const tabPanels = document.querySelectorAll(".tab-panel");
const loginForm = document.getElementById("loginForm");
const loginUsernameInput = document.getElementById("loginUsername");
const loginPasswordInput = document.getElementById("loginPassword");
const loginErrorEl = document.getElementById("loginError");

// registration elements
const registerForm = document.getElementById("registerForm");
const registerUsernameInput = document.getElementById("registerUsername");
const registerPasswordInput = document.getElementById("registerPassword");
const registerPasswordConfirmInput = document.getElementById("registerPasswordConfirm");
const registerErrorEl = document.getElementById("registerError");

const quickRoleButtons = document.querySelectorAll("[data-quick-role]");

// Initialization
initTheme();
initGenres();
loadMoviesFromAPI();
attachEventListeners();
selectDefaultMovie();
// ensure each movie has container for user reviews
// После загрузки фильмов инициализируем пользовательские рецензии
// В новой версии они будут приходить с API, но мы оставляем эту логику для совместимости
MOVIES.forEach((m) => {
  if (!Array.isArray(m.userReviews)) {
    m.userReviews = [];
  } else {
    // normalize existing user reviews ratings to integers
    m.userReviews = m.userReviews.map((r) => ({
      ...r,
      rating: Math.round(Number(r.rating || 0)),
    }));
  }
});

// Функция для загрузки фильмов с API
async function loadMoviesFromAPI() {
  try {
    const response = await fetch(`${API_BASE_URL}/movies`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const moviesData = await response.json();
    
    // Преобразуем данные из API в формат, ожидаемый фронтендом
    MOVIES = moviesData.map(movie => ({
      id: movie.id,
      title: movie.title,
      year: movie.year,
      genre: movie.genre,
      rating: movie.rating,
      poster: movie.poster,
      overview: movie.overview,
      review: movie.review,
      // Преобразуем picks из объектов в массив имен
      picks: movie.picks ? movie.picks.map(pick => pick.name) : [],
      // Добавляем дополнительные поля, если их нет
      extraReviews: [],
      userReviews: []
    }));
    
    // Обновляем UI после загрузки данных
    initGenres();
    renderMovies();
  } catch (error) {
    console.error("Ошибка при загрузке фильмов:", error);
    // В случае ошибки показываем сообщение пользователю
    moviesListEl.innerHTML = '<li class="placeholder-text">Не удалось загрузить фильмы. Попробуйте обновить страницу.</li>';
  }
}

function initTheme() {
  const saved = localStorage.getItem("kinovzor-theme");
  if (saved === "light") {
    body.classList.remove("theme-dark");
    body.classList.add("theme-light");
  } else {
    body.classList.remove("theme-light");
    body.classList.add("theme-dark");
  }
}

function initGenres() {
  const genres = Array.from(new Set(MOVIES.map((m) => m.genre))).sort();
  genres.forEach((g) => {
    const option = document.createElement("option");
    option.value = g;
    option.textContent = g;
    genreSelectEl.appendChild(option);
  });
}

function getFilteredMovies() {
  return MOVIES.filter((movie) => {
    if (currentPick !== "all" && !movie.picks.includes(currentPick)) {
      return false;
    }
    if (currentGenre !== "all" && movie.genre !== currentGenre) {
      return false;
    }
    if (currentRatingFilter !== "all" && movie.rating < Number(currentRatingFilter)) {
      return false;
    }
    if (currentSearch.trim()) {
      const term = currentSearch.trim().toLowerCase();
      if (!movie.title.toLowerCase().includes(term)) return false;
    }
    return true;
  });
}

function renderMovies() {
  moviesListEl.innerHTML = "";
  const movies = getFilteredMovies();

  if (movies.length === 0) {
    const empty = document.createElement("li");
    empty.className = "placeholder-text";
    empty.textContent = "По заданным фильтрам фильмы не найдены.";
    moviesListEl.appendChild(empty);
    movieDetailsEl.classList.add("empty");
    movieDetailsEl.innerHTML =
      '<p class="placeholder-text">Измените фильтры или поиск, чтобы увидеть фильмы.</p>';
    return;
  }

  movies.forEach((movie) => {
    const li = document.createElement("li");
    li.className = "movie-card";
    li.dataset.id = movie.id;

    const posterWrap = document.createElement("div");
    posterWrap.className = "movie-poster-wrapper";
    const posterImg = document.createElement("img");
    posterImg.className = "movie-poster";
    posterImg.src =
      movie.poster || "https://picsum.photos/seed/defaultposter/200/300";
    posterImg.alt = `${movie.title} постер`;
    posterWrap.appendChild(posterImg);

    const bodyWrap = document.createElement("div");
    bodyWrap.className = "movie-card-body";

    const header = document.createElement("div");
    header.className = "movie-card-header";

    const title = document.createElement("div");
    title.className = "movie-title";
    title.textContent = movie.title;

    const ratingBadge = document.createElement("div");
    ratingBadge.className = "badge-rating";
    // render integer ratings
    ratingBadge.textContent = Math.round(Number(movie.rating)).toFixed(0);

    header.appendChild(title);
    header.appendChild(ratingBadge);

    const metaRow = document.createElement("div");
    metaRow.className = "movie-meta";
    metaRow.innerHTML = `
      <span>${movie.year}</span>
      <span>•</span>
      <span>${movie.genre}</span>
    `;

    const footer = document.createElement("div");
    footer.className = "movie-card-footer";

    const picks = document.createElement("div");
    picks.className = "movie-picks";
    movie.picks.forEach((p) => {
      const pickChip = document.createElement("span");
      pickChip.className = "movie-pick-chip";
      pickChip.textContent = getPickLabel(p);
      picks.appendChild(pickChip);
    });

    const rightControls = document.createElement("div");
    rightControls.style.display = "flex";
    rightControls.style.gap = "6px";
    rightControls.style.alignItems = "center";

    const favBtn = document.createElement("button");
    favBtn.className = "fav-button";
    favBtn.title = "Добавить в избранное";
    favBtn.textContent = FAVORITES.has(movie.id) ? "★" : "☆";
    if (FAVORITES.has(movie.id)) favBtn.classList.add("active");

    // prevent whole-card click when toggling favorite
    favBtn.addEventListener("click", (ev) => {
      ev.stopPropagation();
      toggleFavorite(movie.id);
      // update visual immediately for this card
      favBtn.textContent = FAVORITES.has(movie.id) ? "★" : "☆";
      favBtn.classList.toggle("active", FAVORITES.has(movie.id));
    });

    const more = document.createElement("span");
    more.textContent = "Рецензии";
    more.style.cursor = "pointer";

    rightControls.appendChild(favBtn);
    rightControls.appendChild(more);

    footer.appendChild(picks);
    footer.appendChild(rightControls);

    bodyWrap.appendChild(header);
    bodyWrap.appendChild(metaRow);
    bodyWrap.appendChild(footer);

    li.appendChild(posterWrap);
    li.appendChild(bodyWrap);

    // click behavior: on mobile (narrow) toggle in-card expansion, otherwise use details panel
    li.addEventListener("click", () => {
      const isMobile = window.innerWidth <= 540;
      selectedMovieId = movie.id;
      if (isMobile) {
        const already = li.classList.contains("expanded");
        // collapse any other expanded card and remove their expanded content
        document.querySelectorAll(".movie-card.expanded").forEach((c) => {
          if (c !== li) {
            c.classList.remove("expanded");
            const extra = c.querySelector(".mobile-expanded");
            if (extra) extra.remove();
          }
        });
        if (already) {
          li.classList.remove("expanded");
          // remove expanded content
          const extra = li.querySelector(".mobile-expanded");
          if (extra) extra.remove();
        } else {
          li.classList.add("expanded");
          // build mobile expansion content
          const expanded = document.createElement("div");
          expanded.className = "mobile-expanded";
          expanded.style.marginTop = "8px";

          const overviewTitle = document.createElement("div");
          overviewTitle.className = "details-section-title";
          overviewTitle.textContent = "Сюжет";
          const overviewText = document.createElement("div");
          overviewText.className = "details-overview";
          overviewText.textContent = movie.overview || "";

          const reviewTitle = document.createElement("div");
          reviewTitle.className = "details-section-title";
          reviewTitle.textContent = "Рецензии";

          const reviewsContainer = document.createElement("div");

          // combine system + extra + user reviews
          const allReviews = [];
          if (movie.review) {
            allReviews.push({
              author: "КиноВзор",
              role: "system",
              rating: Math.round(Number(movie.rating)),
              text: movie.review,
            });
          }
          if (Array.isArray(movie.extraReviews)) {
            movie.extraReviews.forEach((text) => {
              if (!text) return;
              allReviews.push({
                author: "КиноВзор",
                role: "system",
                rating: Math.round(Number(movie.rating)),
                text,
              });
            });
          }
          if (Array.isArray(movie.userReviews)) {
            movie.userReviews.forEach((r) =>
              allReviews.push({
                author: r.author,
                role: r.role,
                rating: Math.round(Number(r.rating)),
                text: r.text,
              })
            );
          }

          if (allReviews.length === 0) {
            const emptyReview = document.createElement("div");
            emptyReview.className = "placeholder-text";
            emptyReview.textContent =
              "Пока нет рецензий. Станьте первым, кто оценит этот фильм.";
            reviewsContainer.appendChild(emptyReview);
          } else {
            allReviews.forEach((r) => {
            const item = document.createElement("div");
            item.className = "review-item";

            const headerRow = document.createElement("div");
            headerRow.className = "review-header";

            const authorEl = document.createElement("div");
            authorEl.className = "review-author";
            authorEl.textContent = r.author;

            const roleEl = document.createElement("div");
            roleEl.className = "review-role";
            if (r.role === "moderator") {
              roleEl.textContent = "Модератор";
            } else if (r.role === "viewer") {
              roleEl.textContent = "Зритель";
            } else {
              roleEl.textContent = "КиноВзор";
            }

            const ratingEl = document.createElement("div");
            ratingEl.className = "review-rating-badge";
            ratingEl.textContent = `${Math.round(Number(r.rating)).toFixed(0)} ★`;

            headerRow.appendChild(authorEl);
            headerRow.appendChild(roleEl);
            headerRow.appendChild(ratingEl);

            const textEl = document.createElement("div");
            textEl.className = "review-text";
            textEl.textContent = r.text;

            item.appendChild(headerRow);
            item.appendChild(textEl);

            // allow moderators to delete user-submitted reviews (not system reviews)
            if (currentUser && currentUser.role === "moderator" && r.role !== "system") {
              const delBtn = document.createElement("button");
              delBtn.className = "secondary-button";
              delBtn.style.marginTop = "6px";
              delBtn.textContent = "Удалить рецензию";
              delBtn.addEventListener("click", (ev) => {
                ev.stopPropagation();
                // find movie and remove first matching user review by unique properties
                const targetMovie = MOVIES.find((mm) => mm.id === movie.id);
                if (!targetMovie || !Array.isArray(targetMovie.userReviews)) return;
                const idx = targetMovie.userReviews.findIndex(
                  (ur) =>
                    ur.author === r.author &&
                    String(Math.round(Number(ur.rating))) === String(Math.round(Number(r.rating))) &&
                    (ur.text || "") === (r.text || "")
                );
                if (idx >= 0) {
                  targetMovie.userReviews.splice(idx, 1);
                  // refresh UI
                  // if mobile expanded exists, rebuild it by collapsing and reopening
                  document.querySelectorAll(".movie-card.expanded").forEach((c) => {
                    const id = Number(c.dataset.id);
                    if (id === movie.id) {
                      c.classList.remove("expanded");
                      const extra = c.querySelector(".mobile-expanded");
                      if (extra) extra.remove();
                    }
                  });
                  // if details panel currently showing this movie, re-render it
                  if (selectedMovieId === movie.id) {
                    renderMovieDetails(movie.id);
                  }
                  // re-open expanded if on mobile (simple rebuild)
                  const li = document.querySelector(`.movie-card[data-id='${movie.id}']`);
                  if (li && window.innerWidth <= 540) {
                    li.classList.add("expanded");
                    li.click();
                  } else {
                    renderMovies();
                  }
                }
              });
              item.appendChild(delBtn);
            }

            reviewsContainer.appendChild(item);
          });
          }

          expanded.appendChild(overviewTitle);
          expanded.appendChild(overviewText);
          expanded.appendChild(reviewTitle);
          expanded.appendChild(reviewsContainer);

          // if logged in, add a compact review form inside expansion
          if (currentUser) {
            const form = document.createElement("form");
            form.className = "review-form";
            form.style.marginTop = "8px";

            const textRow = document.createElement("div");
            textRow.className = "review-form-row";
            const textLabel = document.createElement("label");
            textLabel.className = "form-label";
            textLabel.textContent = "Ваш отзыв";
            const textArea = document.createElement("textarea");
            textArea.rows = 2;
            textArea.placeholder = "Короткий отзыв...";
            textArea.className = "input";
            textRow.appendChild(textLabel);
            textRow.appendChild(textArea);

            const ratingRow = document.createElement("div");
            ratingRow.className = "review-form-rating-row";
            const ratingLabel = document.createElement("label");
            ratingLabel.className = "form-label";
            ratingLabel.textContent = "Оценка";
            const ratingSelect = document.createElement("select");
            ratingSelect.className = "input review-rating-select";
            for (let v = 10; v >= 1; v--) {
              const opt = document.createElement("option");
              opt.value = v;
              opt.textContent = v;
              ratingSelect.appendChild(opt);
            }
            ratingRow.appendChild(ratingLabel);
            ratingRow.appendChild(ratingSelect);

            const submitBtn = document.createElement("button");
            submitBtn.type = "submit";
            submitBtn.className = "primary-button full-width";
            submitBtn.textContent = "Оставить";

            form.appendChild(textRow);
            form.appendChild(ratingRow);
            form.appendChild(submitBtn);

            form.addEventListener("submit", (ev) => {
              ev.preventDefault();
              const text = textArea.value.trim();
              const rating = Math.round(Number(ratingSelect.value));
              if (!text || !rating) return;

              movie.userReviews.push({
                author: currentUser.username,
                role: currentUser.role,
                rating,
                text,
              });

              // re-render expanded content to show new review
              textArea.value = "";
              ratingSelect.value = "10";
              // collapse any expanded state and reopen this one to refresh
              document.querySelectorAll(".movie-card.expanded").forEach((c) => {
                if (c !== li) {
                  c.classList.remove("expanded");
                  const extra = c.querySelector(".mobile-expanded");
                  if (extra) extra.remove();
                }
              });
              li.classList.remove("expanded");
              const existing = li.querySelector(".mobile-expanded");
              if (existing) existing.remove();
              li.classList.add("expanded");
              // simple approach: call click to rebuild
              li.click();
            });

            expanded.appendChild(form);
          }

          li.appendChild(expanded);
          // ensure details panel also updates for larger viewports if user switches orientation
          renderMovieDetails(movie.id);
        }
      } else {
        renderMovieDetails(movie.id);
      }
    });

    moviesListEl.appendChild(li);
  });
}

function getPickLabel(code) {
  switch (code) {
    case "hits":
      return "Хит";
    case "new":
      return "Новинка";
    case "classic":
      return "Классика";
    default:
      return "";
  }
}

function renderMovieDetails(id) {
  const movie = MOVIES.find((m) => m.id === id);
  if (!movie) return;

  // Убедимся, что у фильма есть массив пользовательских рецензий
  if (!Array.isArray(movie.userReviews)) {
    movie.userReviews = [];
  }

  movieDetailsEl.classList.remove("empty");
  movieDetailsEl.innerHTML = "";

  const wrapper = document.createElement("div");
  wrapper.className = "details-scroll";

  const header = document.createElement("div");
  header.className = "details-header";

  const headerTop = document.createElement("div");
  headerTop.className = "details-header-top";

  const posterWrap = document.createElement("div");
  posterWrap.className = "details-poster-wrapper";
  const posterImg = document.createElement("img");
  posterImg.className = "details-poster";
  posterImg.src =
    movie.poster || "https://picsum.photos/seed/defaultposter/200/300";
  posterImg.alt = `${movie.title} постер`;
  posterWrap.appendChild(posterImg);

  const titleBlockWrap = document.createElement("div");
  titleBlockWrap.style.flex = "1";
  const titleRow = document.createElement("div");
  titleRow.className = "details-title-row";

  const titleBlock = document.createElement("div");
  const titleEl = document.createElement("div");
  titleEl.className = "details-title";
  titleEl.textContent = movie.title;
  const yearEl = document.createElement("div");
  yearEl.className = "details-year";
  yearEl.textContent = movie.year;
  titleBlock.appendChild(titleEl);
  titleBlock.appendChild(yearEl);

  const ratingBadge = document.createElement("div");
  ratingBadge.className = "badge-rating";
  // integer display
  ratingBadge.textContent = Math.round(Number(movie.rating)).toFixed(0);

  // favorite button in details header
  const favDetailBtn = document.createElement("button");
  favDetailBtn.className = "fav-button";
  favDetailBtn.style.marginLeft = "8px";
  favDetailBtn.textContent = FAVORITES.has(movie.id) ? "★" : "☆";
  favDetailBtn.title = FAVORITES.has(movie.id) ? "В избранном" : "Добавить в избранное";
  if (FAVORITES.has(movie.id)) favDetailBtn.classList.add("active");
  favDetailBtn.addEventListener("click", (ev) => {
    ev.stopPropagation();
    toggleFavorite(movie.id);
    favDetailBtn.textContent = FAVORITES.has(movie.id) ? "★" : "☆";
    favDetailBtn.classList.toggle("active", FAVORITES.has(movie.id));
    favDetailBtn.title = FAVORITES.has(movie.id) ? "В избранном" : "Добавить в избранное";
    // keep movies list and details in sync
    renderMovies();
    if (selectedMovieId != null) renderMovieDetails(selectedMovieId);
  });

  const rightWrap = document.createElement("div");
  rightWrap.style.display = "flex";
  rightWrap.style.alignItems = "center";
  rightWrap.style.gap = "8px";
  rightWrap.appendChild(ratingBadge);
  rightWrap.appendChild(favDetailBtn);

  titleRow.appendChild(titleBlock);
  titleRow.appendChild(rightWrap);

  const metaRow = document.createElement("div");
  metaRow.className = "details-meta-row";
  metaRow.innerHTML = `
    <span>${movie.genre}</span>
    <span>•</span>
    <span>${movie.year}</span>
  `;

  const tagsRow = document.createElement("div");
  tagsRow.className = "details-tags";
  movie.picks.forEach((p) => {
    const chip = document.createElement("span");
    chip.className = "movie-pick-chip";
    chip.textContent = getPickLabel(p);
    tagsRow.appendChild(chip);
  });

  titleBlockWrap.appendChild(titleRow);
  titleBlockWrap.appendChild(metaRow);
  titleBlockWrap.appendChild(tagsRow);

  headerTop.appendChild(posterWrap);
  headerTop.appendChild(titleBlockWrap);

  header.appendChild(headerTop);

  const overviewTitle = document.createElement("div");
  overviewTitle.className = "details-section-title";
  overviewTitle.textContent = "Сюжет";

  const overviewText = document.createElement("div");
  overviewText.className = "details-overview";
  overviewText.textContent = movie.overview;

  const reviewTitle = document.createElement("div");
  reviewTitle.className = "details-section-title";
  reviewTitle.textContent = "Рецензии";

  const reviewsContainer = document.createElement("div");

  // build full review list: базовые + пользовательские
  const allReviews = [];

  if (movie.review) {
    allReviews.push({
      author: "КиноВзор",
      role: "system",
      rating: Math.round(Number(movie.rating)),
      text: movie.review,
    });
  }

  if (Array.isArray(movie.extraReviews)) {
    movie.extraReviews.forEach((text) => {
      if (!text) return;
      allReviews.push({
        author: "КиноВзор",
        role: "system",
        rating: Math.round(Number(movie.rating)),
        text,
      });
    });
  }

  movie.userReviews.forEach((r) =>
    allReviews.push({
      author: r.author,
      role: r.role === "admin" ? "moderator" : r.role,
      rating: Math.round(Number(r.rating)),
      text: r.text,
    })
  );

  if (allReviews.length === 0) {
    const emptyReview = document.createElement("div");
    emptyReview.className = "placeholder-text";
    emptyReview.textContent =
      "Пока нет рецензий. Станьте первым, кто оценит этот фильм.";
    reviewsContainer.appendChild(emptyReview);
  } else {
    allReviews.forEach((r) => {
      const item = document.createElement("div");
      item.className = "review-item";

      const headerRow = document.createElement("div");
      headerRow.className = "review-header";

      const authorEl = document.createElement("div");
      authorEl.className = "review-author";
      authorEl.textContent = r.author;

      const roleEl = document.createElement("div");
      roleEl.className = "review-role";
      if (r.role === "moderator") {
        roleEl.textContent = "Модератор";
      } else if (r.role === "viewer") {
        roleEl.textContent = "Зритель";
      } else {
        roleEl.textContent = "КиноВзор";
      }

      const ratingEl = document.createElement("div");
      ratingEl.className = "review-rating-badge";
      ratingEl.textContent = `${Math.round(Number(r.rating)).toFixed(0)} ★`;

      headerRow.appendChild(authorEl);
      headerRow.appendChild(roleEl);
      headerRow.appendChild(ratingEl);

      const textEl = document.createElement("div");
      textEl.className = "review-text";
      textEl.textContent = r.text;

      item.appendChild(headerRow);
      item.appendChild(textEl);

      // moderator can delete non-system reviews
      if (currentUser && currentUser.role === "moderator" && r.role !== "system") {
        const delBtn = document.createElement("button");
        delBtn.className = "secondary-button";
        delBtn.style.marginTop = "6px";
        delBtn.textContent = "Удалить рецензию";
        delBtn.addEventListener("click", (ev) => {
          ev.stopPropagation();
          const targetMovie = MOVIES.find((mm) => mm.id === movie.id);
          if (!targetMovie || !Array.isArray(targetMovie.userReviews)) return;
          const idx = targetMovie.userReviews.findIndex(
            (ur) =>
              ur.author === r.author &&
              String(Math.round(Number(ur.rating))) === String(Math.round(Number(r.rating))) &&
              (ur.text || "") === (r.text || "")
          );
          if (idx >= 0) {
            targetMovie.userReviews.splice(idx, 1);
            renderMovieDetails(movie.id);
            renderMovies();
          }
        });
        item.appendChild(delBtn);
      }

      reviewsContainer.appendChild(item);
    });
  }

  wrapper.appendChild(header);
  wrapper.appendChild(overviewTitle);
  wrapper.appendChild(overviewText);
  wrapper.appendChild(reviewTitle);
  wrapper.appendChild(reviewsContainer);

  // форма для добавления рецензии для залогиненных
  if (currentUser) {
    const form = document.createElement("form");
    form.className = "review-form";

    const formTitle = document.createElement("div");
    formTitle.className = "details-section-title";
    formTitle.textContent = "Добавить рецензию";
    form.appendChild(formTitle);

    const textRow = document.createElement("div");
    textRow.className = "review-form-row";
    const textLabel = document.createElement("label");
    textLabel.className = "form-label";
    textLabel.textContent = "Ваш отзыв";
    const textArea = document.createElement("textarea");
    textArea.rows = 3;
    textArea.placeholder = "Поделитесь впечатлениями о фильме...";
    textArea.className = "input";
    textRow.appendChild(textLabel);
    textRow.appendChild(textArea);

    const ratingRow = document.createElement("div");
    ratingRow.className = "review-form-rating-row";
    const ratingLabel = document.createElement("label");
    ratingLabel.className = "form-label";
    ratingLabel.textContent = "Оценка";
    const ratingSelect = document.createElement("select");
    ratingSelect.className = "input review-rating-select";
    for (let v = 10; v >= 1; v--) {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      ratingSelect.appendChild(opt);
    }
    ratingRow.appendChild(ratingLabel);
    ratingRow.appendChild(ratingSelect);

    const submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.className = "primary-button full-width";
    submitBtn.textContent = "Оставить рецензию";

    form.appendChild(textRow);
    form.appendChild(ratingRow);
    form.appendChild(submitBtn);

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = textArea.value.trim();
      // store integer rating
      const rating = Math.round(Number(ratingSelect.value));
      if (!text || !rating) return;

      movie.userReviews.push({
        author: currentUser.username,
        role: currentUser.role,
        rating,
        text,
      });

      textArea.value = "";
      ratingSelect.value = "10";
      renderMovieDetails(movie.id);
    });

    wrapper.appendChild(form);
  }

  movieDetailsEl.appendChild(wrapper);
}

function selectDefaultMovie() {
  const list = getFilteredMovies();
  if (list.length > 0) {
    selectedMovieId = list[0].id;
    renderMovieDetails(selectedMovieId);
  }
}

function attachEventListeners() {
  searchInputEl.addEventListener("input", (e) => {
    currentSearch = e.target.value;
    renderMovies();
    selectDefaultMovie();
  });

  genreSelectEl.addEventListener("change", (e) => {
    currentGenre = e.target.value;
    renderMovies();
    selectDefaultMovie();
  });

  ratingButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      ratingButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentRatingFilter = btn.dataset.rating;
      renderMovies();
      selectDefaultMovie();
    });
  });

  pickButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      pickButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentPick = btn.dataset.pick;
      renderMovies();
      selectDefaultMovie();
    });
  });

  themeToggleBtn.addEventListener("click", () => {
    const isDark = body.classList.contains("theme-dark");
    if (isDark) {
      body.classList.remove("theme-dark");
      body.classList.add("theme-light");
      localStorage.setItem("kinovzor-theme", "light");
    } else {
      body.classList.remove("theme-light");
      body.classList.add("theme-dark");
      localStorage.setItem("kinovzor-theme", "dark");
    }
  });

  authButton.addEventListener("click", openAuthModal);
  closeAuthModalBtn.addEventListener("click", closeAuthModal);
  authModal.addEventListener("click", (e) => {
    if (e.target === authModal || e.target.classList.contains("modal-backdrop")) {
      closeAuthModal();
    }
  });

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;
      tabButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      tabPanels.forEach((panel) => {
        panel.classList.toggle("active", panel.dataset.panel === tab);
      });
    });
  });

  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleLogin();
  });

  // registration submit
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      e.preventDefault();
      handleRegister();
    });
  }

  quickRoleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const role = btn.dataset.quickRole;
      handleQuickLogin(role);
    });
  });

  logoutButton.addEventListener("click", handleLogout);

  closeProfileModalBtn.addEventListener("click", closeProfileModal);
  profileModal.addEventListener("click", (e) => {
    if (e.target === profileModal || e.target.classList.contains("modal-backdrop")) {
      closeProfileModal();
    }
  });

  // open profile by clicking userBadge (also allow authButton area for safety)
  userBadge.addEventListener("click", (e) => {
    // ensure clicks on logout icon still work (stopPropagation there)
    openProfileModal();
  });

  adminAddForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleAdminAddMovie();
  });
}

function openAuthModal() {
  authModal.classList.remove("hidden");
  loginErrorEl.classList.add("hidden");
  loginErrorEl.textContent = "";
  setTimeout(() => {
    loginUsernameInput.focus();
  }, 50);
}

function closeAuthModal() {
  authModal.classList.add("hidden");
}

function handleLogin() {
  const username = loginUsernameInput.value.trim();
  const password = loginPasswordInput.value;

  const user = USERS.find(
    (u) => u.username === username && u.password === password
  );

  if (!user) {
    loginErrorEl.textContent = "Неверный логин или пароль.";
    loginErrorEl.classList.remove("hidden");
    return;
  }

  currentUser = { username: user.username, role: user.role };
  updateAuthUI();
  closeAuthModal();
}

function handleQuickLogin(role) {
  if (role !== "viewer" && role !== "moderator") return;
  currentUser = {
    username: role === "viewer" ? "Гость" : "Модер-гость",
    role: role,
  };
  updateAuthUI();
  closeAuthModal();
}

// simple registration handler: creates a new viewer user, prevents duplicate usernames
function handleRegister() {
  if (!registerUsernameInput || !registerPasswordInput || !registerPasswordConfirmInput) return;

  const username = registerUsernameInput.value.trim();
  const pass = registerPasswordInput.value;
  const pass2 = registerPasswordConfirmInput.value;

  registerErrorEl.classList.add("hidden");
  registerErrorEl.textContent = "";

  if (!username || !pass) {
    registerErrorEl.textContent = "Введите логин и пароль.";
    registerErrorEl.classList.remove("hidden");
    return;
  }

  if (pass !== pass2) {
    registerErrorEl.textContent = "Пароли не совпадают.";
    registerErrorEl.classList.remove("hidden");
    return;
  }

  // check duplicate (case-insensitive)
  const exists = USERS.some((u) => u.username.toLowerCase() === username.toLowerCase());
  if (exists) {
    registerErrorEl.textContent = "Пользователь с таким логином уже существует.";
    registerErrorEl.classList.remove("hidden");
    return;
  }

  // add new user as viewer
  USERS.push({ username, password: pass, role: "viewer" });

  // auto-login the new user
  currentUser = { username, role: "viewer" };
  updateAuthUI();

  // clear and close modal
  registerForm.reset();
  closeAuthModal();
}

function handleLogout() {
  currentUser = null;
  updateAuthUI();
}

function updateAuthUI() {
  if (currentUser) {
    authButton.classList.add("hidden");
    userBadge.classList.remove("hidden");
    userNameEl.textContent = currentUser.username;
    userRoleEl.textContent =
      currentUser.role === "moderator" ? "Роль: модератор" : "Роль: зритель";
    if (currentUser.role === "moderator") {
      adminPanel.classList.remove("hidden");
    } else {
      adminPanel.classList.add("hidden");
    }
    // make userBadge interactive (hint)
    userBadge.style.cursor = "pointer";
  } else {
    authButton.classList.remove("hidden");
    userBadge.classList.add("hidden");
    userNameEl.textContent = "";
    userRoleEl.textContent = "";
    adminPanel.classList.add("hidden");
    userBadge.style.cursor = "";
    // ensure profile modal closes when logged out
    closeProfileModal();
  }

  // пересчитать форму рецензии при смене авторизации
  if (selectedMovieId != null) {
    renderMovieDetails(selectedMovieId);
  }
}

function handleAdminAddMovie() {
  // only moderators can add movies now
  if (!currentUser || currentUser.role !== "moderator") return;

  const title = adminTitleInput.value.trim();
  const year = Number(adminYearInput.value);
  const rating = Number(adminRatingInput.value);
  const genre = adminGenreInput.value.trim() || "Драма";
  const poster = adminPosterInput.value.trim();
  const overview =
    adminOverviewInput.value.trim() || "Описание будет добавлено позже.";
  const review1 =
    adminReview1Input.value.trim() || "Рецензия будет добавлена позже.";
  const review2 = adminReview2Input.value.trim();

  const picks = [];
  adminPanel
    .querySelectorAll(".admin-picks input[type='checkbox']")
    .forEach((cb) => {
      if (cb.checked) picks.push(cb.value);
    });

  if (!title || !year || !rating) {
    return;
  }

  const newId =
    MOVIES.reduce((max, m) => (m.id > max ? m.id : max), 0) + 1;

  const newMovie = {
    id: newId,
    title,
    year,
    genre,
    rating,
    picks: picks.length ? picks : ["new"],
    poster: poster || `https://picsum.photos/seed/film${newId}/200/300`,
    overview,
    review: review1,
    extraReviews: review2 ? [review2] : [],
    userReviews: [],
  };

  MOVIES.push(newMovie);
  initGenres();
  renderMovies();
  selectedMovieId = newMovie.id;
  renderMovieDetails(newMovie.id);

  adminAddForm.reset();
}

// toggle favorite helper
function toggleFavorite(id) {
  const iid = Number(id);
  if (FAVORITES.has(iid)) {
    FAVORITES.delete(iid);
  } else {
    FAVORITES.add(iid);
  }
  localStorage.setItem("kinovzor-favs", JSON.stringify(Array.from(FAVORITES)));
  // keep movies list and details in sync
  renderMovies();
  if (selectedMovieId != null) renderMovieDetails(selectedMovieId);
}

// Profile modal functions
function openProfileModal() {
  if (!currentUser) {
    // if not logged, open auth modal instead
    openAuthModal();
    return;
  }
  profileModal.classList.remove("hidden");
  renderFavoritesList();
}

function closeProfileModal() {
  profileModal.classList.add("hidden");
}

// render favorites inside profile
function renderFavoritesList() {
  favoritesListEl.innerHTML = "";
  const favIds = Array.from(FAVORITES);
  if (!favIds.length) {
    profileContentEl.querySelector(".placeholder-text").textContent = "У вас пока нет избранных фильмов.";
    return;
  } else {
    const ph = profileContentEl.querySelector(".placeholder-text");
    if (ph) ph.remove();
  }

  // build compact cards similar to movie list but simplified
  favIds.forEach((id) => {
    const movie = MOVIES.find((m) => m.id === Number(id));
    if (!movie) return;

    const li = document.createElement("li");
    li.className = "movie-card";
    li.style.width = "100%";
    li.style.display = "flex";
    li.style.flexDirection = "row";
    li.style.alignItems = "center";
    li.style.gap = "10px";
    li.dataset.id = movie.id;

    const poster = document.createElement("div");
    poster.className = "movie-poster-wrapper";
    poster.style.width = "72px";
    poster.style.height = "100px";
    poster.style.flex = "0 0 auto";
    poster.style.borderRadius = "8px";
    const img = document.createElement("img");
    img.className = "movie-poster";
    img.src = movie.poster;
    img.alt = movie.title;
    img.style.width = "100%";
    img.style.height = "100%";
    img.style.objectFit = "cover";
    poster.appendChild(img);

    const info = document.createElement("div");
    info.style.flex = "1";
    info.style.display = "flex";
    info.style.flexDirection = "column";
    info.style.gap = "4px";
    const title = document.createElement("div");
    title.textContent = movie.title;
    title.style.fontWeight = "600";
    title.style.fontSize = "13px";
    const meta = document.createElement("div");
    meta.textContent = `${movie.year} • ${movie.genre}`;
    meta.style.fontSize = "12px";
    meta.style.color = "var(--color-muted)";

    info.appendChild(title);
    info.appendChild(meta);

    const actions = document.createElement("div");
    actions.style.display = "flex";
    actions.style.flexDirection = "column";
    actions.style.gap = "6px";
    actions.style.alignItems = "flex-end";

    const openBtn = document.createElement("button");
    openBtn.className = "secondary-button";
    openBtn.textContent = "Открыть";
    openBtn.addEventListener("click", (ev) => {
      ev.stopPropagation();
      // show in details panel and close profile
      selectedMovieId = movie.id;
      renderMovieDetails(movie.id);
      closeProfileModal();
    });

    const removeBtn = document.createElement("button");
    removeBtn.className = "secondary-button";
    removeBtn.textContent = "Убрать";
    removeBtn.addEventListener("click", (ev) => {
      ev.stopPropagation();
      toggleFavorite(movie.id);
      // re-render favorites list
      renderFavoritesList();
    });

    actions.appendChild(openBtn);
    actions.appendChild(removeBtn);

    li.appendChild(poster);
    li.appendChild(info);
    li.appendChild(actions);

    favoritesListEl.appendChild(li);
  });
}