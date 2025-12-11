from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import logging

# Импортируем все роутеры из app.api
from app.api import (
    auth,
    movies,
    movies_real,
    reviews,
    users,
    picks,
    movie_picks,
    movie_stats,
    roles,
    favorites,
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title="КиноВзор API",
    description="API для веб-сайта КиноВзор с рецензиями и подборками фильмов",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Получаем абсолютный путь к директории проекта
BASE_DIR = Path(__file__).parent

# Монтирование статических файлов
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Статические файлы подключены из {static_dir}")

# ============================================================================
# ПОДКЛЮЧЕНИЕ ВСЕХ МАРШРУТОВ
# ============================================================================

# Подключение роутеров API с префиксами версий
api_v1_prefix = "/api/v1"

# Аутентификация и авторизация
app.include_router(
    auth.router,
    prefix=f"{api_v1_prefix}/auth",
    tags=["Аутентификация"]
)
logger.info("Роутер auth подключен")

app.include_router(
    roles.router,
    prefix=f"{api_v1_prefix}/roles",
    tags=["Роли"]
)
logger.info("Роутер roles подключен")

# Фильмы
app.include_router(
    movies.router,
    prefix=f"{api_v1_prefix}/movies",
    tags=["Фильмы"]
)
logger.info("Роутер movies подключен")

app.include_router(
    movies_real.router,
    prefix=f"{api_v1_prefix}/movies-real",
    tags=["Фильмы (Real)"]
)
logger.info("Роутер movies_real подключен")

# Рецензии
app.include_router(
    reviews.router,
    prefix=f"{api_v1_prefix}/reviews",
    tags=["Рецензии"]
)
logger.info("Роутер reviews подключен")

# Пользователи
app.include_router(
    users.router,
    prefix=f"{api_v1_prefix}/users",
    tags=["Пользователи"]
)
logger.info("Роутер users подключен")

# Подборки
app.include_router(
    picks.router,
    prefix=f"{api_v1_prefix}/picks",
    tags=["Подборки"]
)
logger.info("Роутер picks подключен")

# Связь фильмов и подборок
app.include_router(
    movie_picks.router,
    prefix=f"{api_v1_prefix}/movie-picks",
    tags=["Фильмы и подборки"]
)
logger.info("Роутер movie_picks подключен")

# Статистика по фильмам
app.include_router(
    movie_stats.router,
    prefix=f"{api_v1_prefix}/movie-stats",
    tags=["Статистика фильмов"]
)
logger.info("Роутер movie_stats подключен")

# Избранные фильмы
app.include_router(
    favorites.router,
    prefix=f"{api_v1_prefix}/favorites",
    tags=["Избранные фильмы"]
)
logger.info("Роутер favorites подключен")

# ============================================================================
# ОСНОВНЫЕ МАРШРУТЫ
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница приложения"""
    templates_dir = BASE_DIR / "templates"
    if templates_dir.exists():
        index_path = templates_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
    return HTMLResponse(
        content="<h1>КиноВзор API</h1><p>API работает. Смотрите документацию на /api/docs</p>"
    )

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "ok",
        "message": "КиноВзор API работает нормально",
        "version": "1.0.0"
    }

@app.get("/api")
async def api_root():
    """Информация об API"""
    return {
        "title": "КиноВзор API",
        "version": "1.0.0",
        "docs_url": "/api/docs",
        "redoc_url": "/api/redoc",
        "openapi_url": "/api/openapi.json"
    }

# ============================================================================
# ОБРАБОТКА ОШИБОК И СОБЫТИЯ ЖИЗНЕННОГО ЦИКЛА
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """События при запуске приложения"""
    logger.info("="*60)
    logger.info("КиноВзор API запущен")
    logger.info("Все роутеры успешно подключены")
    logger.info("Документация доступна на /api/docs")
    logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке приложения"""
    logger.info("КиноВзор API остановлен")

# ============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        reload_dirs=["app"]
    )
