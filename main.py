import uvicorn
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.database.database import engine, Base, init_db as init_database
from app.config import settings

# Импорт роутеров
from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as roles_router
from app.api.movies import router as movies_router
from app.api.reviews import router as reviews_router
from app.api.users import router as users_router
from app.api.picks import router as picks_router
from app.api.movie_picks import router as movie_picks_router
from app.api.movie_stats import router as movie_stats_router



from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_items():
    return {"message": "No auth required"}

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения
    """
    # Startup логика
    logger.info(f"🚀 Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Инициализация базы данных
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы базы данных созданы")
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")
        raise
    
    logger.info("✅ Приложение успешно запущено")
    logger.info(f"📖 API документация: http://localhost:8000{settings.api_prefix}/docs")
    logger.info(f"📖 ReDoc документация: http://localhost:8000{settings.api_prefix}/redoc")
    
    # Проверяем наличие папок для фронтенда
    templates_dir = current_dir / "templates"
    static_dir = current_dir / "static"
    
    if not templates_dir.exists():
        logger.warning(f"⚠️ Директория templates не найдена: {templates_dir}")
        templates_dir.mkdir(exist_ok=True)
        logger.info("✅ Создана директория templates")
        
        # Создаем простой index.html если его нет
        index_file = templates_dir / "index.html"
        if not index_file.exists():
            simple_html = """<!DOCTYPE html>
<html>
<head>
    <title>KinoVzor</title>
    <link rel="stylesheet" href="/static/styles/style.css">
</head>
<body>
    <h1>KinoVzor Backend is Running!</h1>
    <p>API is available at <a href="/api">/api</a></p>
    <p>API Docs: <a href="/docs">/docs</a></p>
</body>
</html>"""
            index_file.write_text(simple_html, encoding='utf-8')
            logger.info("✅ Создан базовый index.html")
    
    if not static_dir.exists():
        logger.warning(f"⚠️ Директория static не найдена: {static_dir}")
        static_dir.mkdir(exist_ok=True)
        logger.info("✅ Создана директория static")
    
    yield
    
    # Shutdown логика
    logger.info("🛑 Остановка KinoVzor API...")

# Создание приложения FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Movie database application",
    contact={
        "name": "KinoVzor Team",
        "url": "https://github.com/username/kinovzor",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    swagger_ui_oauth2_redirect_url=None,
    swagger_ui_init_oauth=None,
    lifespan=lifespan,
)

# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# ---------- Настройка статических файлов и шаблонов ----------
# Определяем пути к папкам со статикой и шаблонами
STATIC_DIR = current_dir / "static"
TEMPLATES_DIR = current_dir / "templates"

# Монтируем статические файлы (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Настраиваем шаблоны Jinja2
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ---------- Эндпоинты для фронтенда ----------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request):
    """
    Главная страница фронтенда
    """
    try:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "KinoVzor - Кинопортал",
                "api_prefix": settings.api_prefix or "/api/v1"
            }
        )
    except Exception as e:
        # Если шаблон не найден, возвращаем простую HTML страницу
        from fastapi.responses import PlainTextResponse
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KinoVzor</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>KinoVzor Backend API</h1>
            <p>Frontend template not found. The API is running correctly.</p>
            <ul>
                <li><a href="/api">API Information</a></li>
                <li><a href="/docs">Swagger Documentation</a></li>
                <li><a href="/redoc">ReDoc Documentation</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
            <p>To add frontend, create 'index.html' in templates folder.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)

# Включение роутеров API
app.include_router(sample_router, tags=["sample"])
app.include_router(auth_router, tags=["authentication"], prefix=settings.api_prefix)
app.include_router(roles_router, tags=["roles"], prefix=settings.api_prefix)
app.include_router(movies_router, tags=["movies"], prefix=settings.api_prefix)
app.include_router(reviews_router, tags=["reviews"], prefix=settings.api_prefix)
app.include_router(users_router, tags=["users"], prefix=settings.api_prefix)
app.include_router(picks_router, tags=["picks"], prefix=settings.api_prefix)
app.include_router(movie_stats_router, prefix=settings.api_prefix)
app.include_router(movie_picks_router, prefix=settings.api_prefix)

# Глобальные обработчики ошибок
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"detail": "Ресурс не найден"},
    )

@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )

# Перенаправления для удобства (от старых путей)
@app.get("/docs", include_in_schema=False)
async def redirect_docs():
    """Перенаправление со старого пути /docs на новый"""
    return RedirectResponse(url=f"{settings.api_prefix}/docs")

@app.get("/redoc", include_in_schema=False)
async def redirect_redoc():
    """Перенаправление со старого пути /redoc на новый"""
    return RedirectResponse(url=f"{settings.api_prefix}/redoc")

@app.get("/openapi.json", include_in_schema=False)
async def redirect_openapi():
    """Перенаправление со старого пути /openapi.json на новый"""
    return RedirectResponse(url=f"{settings.api_prefix}/openapi.json")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint - возвращает простой PNG или ICO"""
    # Если файл есть в static папке, возвращаем его
    favicon_path = current_dir / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")
    # Иначе просто возвращаем пустой ответ 204
    from fastapi import Response
    return Response(status_code=204)

# ---------- корневой эндпоинт ----------
@app.get("/api", tags=["monitoring"], include_in_schema=True)
async def api_root():
    """
    Информация о API (теперь доступна по /api вместо /)
    """
    return {
        "app": settings.project_name,
        "version": settings.project_version,
        "status": "running",
        "frontend": "/",
        "documentation": {
            "swagger": f"{settings.api_prefix}/docs",
            "redoc": f"{settings.api_prefix}/redoc",
            "openapi": f"{settings.api_prefix}/openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "api_base": settings.api_prefix,
            "auth": f"{settings.api_prefix}/auth",
            "movies": f"{settings.api_prefix}/movies",
            "reviews": f"{settings.api_prefix}/reviews",
            "users": f"{settings.api_prefix}/users",
            "roles": f"{settings.api_prefix}/roles",
            "picks": f"{settings.api_prefix}/picks",
        }
    }

@app.get("/health", tags=["monitoring"])
async def health_check():
    """
    Проверка состояния приложения
    """
    import psutil
    
    # Базовая информация о системе
    system_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": settings.project_name,
        "version": settings.project_version,
        "environment": "development" if settings.debug else "production",
    }
    
    # Информация о памяти
    try:
        memory = psutil.virtual_memory()
        system_info["memory"] = {
            "total": f"{memory.total // (1024**2)} MB",
            "available": f"{memory.available // (1024**2)} MB",
            "percent": f"{memory.percent}%",
        }
    except:
        system_info["memory"] = "N/A"
    
    # Информация о CPU
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        system_info["cpu"] = {
            "percent": f"{cpu_percent}%",
            "cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
        }
    except:
        system_info["cpu"] = "N/A"
    
    # Информация о диске
    try:
        disk = psutil.disk_usage('/')
        system_info["disk"] = {
            "total": f"{disk.total // (1024**3)} GB",
            "free": f"{disk.free // (1024**3)} GB",
            "percent": f"{disk.percent}%",
        }
    except:
        system_info["disk"] = "N/A"
    
    return system_info

@app.get("/info", tags=["monitoring"], include_in_schema=False)
async def app_info():
    """
    Подробная информация о приложении
    """
    import sys
    import platform
    
    return {
        "app": {
            "name": settings.project_name,
            "version": settings.project_version,
            "debug": settings.debug,
            "api_prefix": settings.api_prefix,
        },
        "python": {
            "version": sys.version,
            "implementation": platform.python_implementation(),
        },
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "database": {
            "url": "configured" if settings.database_url else "not configured",
            "type": "sqlite" if "sqlite" in settings.database_url else "postgresql",
        },
        "security": {
            "jwt_algorithm": settings.algorithm,
            "token_expire_minutes": settings.access_token_expire_minutes,
        }
    }

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=True,
    )