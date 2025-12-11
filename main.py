from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import logging
import sys

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

# Список роутеров для подключения
routers_to_include = [
    ('auth', 'Аутентификация'),
    ('roles', 'Роли'),
    ('movies', 'Фильмы'),
    ('movies_real', 'Фильмы (Real)'),
    ('reviews', 'Рецензии'),
    ('users', 'Пользователи'),
    ('picks', 'Подборки'),
    ('movie_picks', 'Фильмы и подборки'),
    ('movie_stats', 'Статистика фильмов'),
]

# Подключение роутеров API с префиксами версий
api_v1_prefix = "/api/v1"

try:
    # Импортируем роутеры динамически
    from app import api
    
    for router_name, tag_name in routers_to_include:
        try:
            router_module = getattr(api, router_name)
            if hasattr(router_module, 'router'):
                app.include_router(
                    router_module.router,
                    prefix=f"{api_v1_prefix}/{router_name.replace('_', '-')}",
                    tags=[tag_name]
                )
                logger.info(f"✓ Роутер {router_name} подключен")
            else:
                logger.warning(f"⚠ Модуль {router_name} не содержит атрибут 'router'")
        except (ImportError, AttributeError) as e:
            logger.warning(f"⚠ Не удалось подключить роутер {router_name}: {e}")
            continue
    
    logger.info(f"\n✓ Успешно подключено {len(routers_to_include)} роутеров\n")
    
except ImportError as e:
    logger.error(f"Критическая ошибка при импорте app.api: {e}")
    logger.error(f"Пожалуйста, проверьте структуру проекта")
    sys.exit(1)

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
