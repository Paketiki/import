from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import logging
import importlib
from contextlib import asynccontextmanager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Переменная для хранения количества загруженных роутеров
successfully_loaded = 0

# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # STARTUP
    logger.info("="*60)
    logger.info("КиноВзор API запущен")
    logger.info(f"Подключено {successfully_loaded} роутеров")
    logger.info("Документация доступна на /api/docs")
    logger.info("="*60)
    
    yield
    
    # SHUTDOWN
    logger.info("КиноВзор API остановлен")

# Инициализация FastAPI приложения с lifespan
app = FastAPI(
    title="КиноВзор API",
    description="API для веб-сайта КиноВзор с рецензиями и подборками фильмов",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
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

# Список роутеров для подключения
routers_config = [
    ('app.api.auth', 'auth', 'Аутентификация'),
    ('app.api.roles', 'roles', 'Роли'),
    ('app.api.movies', 'movies', 'Фильмы'),
    ('app.api.movies_real', 'movies_real', 'Фильмы (Real)'),
    ('app.api.reviews', 'reviews', 'Рецензии'),
    ('app.api.users', 'users', 'Пользователи'),
    ('app.api.picks', 'picks', 'Подборки'),
    ('app.api.movie_picks', 'movie_picks', 'Фильмы и подборки'),
    ('app.api.movie_stats', 'movie_stats', 'Статистика фильмов'),
]

# Подключение роутеров API с префиксами версий
api_v1_prefix = "/api/v1"

for module_path, router_name, tag_name in routers_config:
    try:
        # Импортируем модуль динамически
        router_module = importlib.import_module(module_path)
        
        # Проверяем наличие router'a
        if hasattr(router_module, 'router'):
            app.include_router(
                router_module.router,
                prefix=f"{api_v1_prefix}/{router_name.replace('_', '-')}",
                tags=[tag_name]
            )
            logger.info(f"✓ Роутер {router_name} подключен")
            successfully_loaded += 1
        else:
            logger.warning(f"⚠ Модуль {router_name} не содержит 'router'")
    except ImportError as e:
        logger.warning(f"⚠ Не удалось импортировать {module_path}: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка при подключении {router_name}: {e}")

logger.info(f"\n✓ Подключено {successfully_loaded}/{len(routers_config)} роутеров\n")

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
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Запускаем приложение без параметра reload в cli
    # Используем строку импорта для работы reload с Windows
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
