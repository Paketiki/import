from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import logging
from contextlib import asynccontextmanager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Переменная для хранения количества загруженных маршрутов
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
    logger.info(f"Подключено {successfully_loaded} маршрутизаторов")
    logger.info("Документация доступна на /api/docs")
    logger.info("="*60)
    
    yield
    
    # SHUTDOWN
    logger.info("КиноВзор API остановлен")

# Инициализация FastAPI приложения с lifespan
app = FastAPI(
    title="КиноВзор API",
    description="API для веб-сайта КиноВзор с фильмами, отзывами и избранным",
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
# ПОДКЛЮЧЕНИЕ МАРШРУТОВ
# ============================================================================

# Импортируем только нужные маршруты
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.main_api import router as main_api_router

# Подключение маршрутов
api_v1_prefix = "/api/v1"

try:
    # Auth маршруты
    app.include_router(
        auth_router,
        prefix=f"{api_v1_prefix}/auth",
        tags=["Authentication"]
    )
    logger.info("✓ Маршрут auth подключен")
    successfully_loaded += 1
except Exception as e:
    logger.error(f"❌ Ошибка при подключении auth: {e}")

try:
    # Users маршруты
    app.include_router(
        users_router,
        prefix=f"{api_v1_prefix}/users",
        tags=["Users"]
    )
    logger.info("✓ Маршрут users подключен")
    successfully_loaded += 1
except Exception as e:
    logger.error(f"❌ Ошибка при подключении users: {e}")

try:
    # Основной API маршрут (фильмы, отзывы, избранное)
    app.include_router(
        main_api_router,
        prefix=f"{api_v1_prefix}",
        tags=["Main API"]
    )
    logger.info("✓ Маршрут main_api подключен")
    successfully_loaded += 1
except Exception as e:
    logger.error(f"❌ Ошибка при подключении main_api: {e}")

logger.info(f"\n✓ Подключено {successfully_loaded}/3 маршрутизаторов\n")

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
    
    # Запускаем приложение с использованием строки импорта для поддержки reload
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
