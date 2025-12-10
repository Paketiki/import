# main.py - ОБНОВЛЕННАЯ ВЕРСИЯ
import uvicorn
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.database.database import engine, Base, get_db, init_db as init_database
from app.config import settings

# Импорт роутеров
from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as roles_router
from app.api.movies import router as movies_router
from app.api.movie_picks import router as movie_picks_router
from app.api.reviews import router as reviews_router
from app.api.users import router as users_router
from app.api.movie_stats import router as movie_stats_router
from app.api.picks import router as picks_router

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
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
    
    # Асинхронная инициализация базы данных
    try:
        await init_database()  # Используем асинхронную функцию
        logger.info("✅ Таблицы базы данных созданы")
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")
        raise
    
    logger.info("✅ Приложение успешно запущено")
    logger.info(f"API документация: http://localhost:{settings.PORT}/docs")
    logger.info(f"ReDoc документация: http://localhost:{settings.PORT}/redoc")
    
    yield
    
    # Shutdown логика
    logger.info("🛑 Остановка KinoVzor API...")

# Создание приложения FastAPI ТОЛЬКО ОДИН РАЗ
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
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_oauth2_redirect_url=None,
    swagger_ui_init_oauth=None,
    swagger_ui_parameters={"deepLinking": False, "displayOperationId": False},
    lifespan=lifespan,
)

# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обработчик для OPTIONS запросов
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

# ---------- Настройка статических файлов ----------
# Создаем папки если их нет
static_dir = current_dir / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
    (static_dir / "js").mkdir(exist_ok=True)
    (static_dir / "styles").mkdir(exist_ok=True)
    (static_dir / "images").mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Создаем объект templates
templates_dir = current_dir / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# ---------- Основные эндпоинты ----------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request):
    """
    Главная страница фронтенда
    """
    try:
        index_path = current_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        
        # Используем шаблон как запасной вариант
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "KinoVzor - Кинопортал"}
        )
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>KinoVzor</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #0a0a0a; color: white; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #ff7a1a; }
                ul { list-style: none; padding: 0; }
                li { margin: 10px 0; }
                a { color: #ff7a1a; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>KinoVzor Backend is Running!</h1>
                <p>Frontend index.html not found in root directory.</p>
                <p>Available endpoints:</p>
                <ul>
                    <li><a href="/api/v1/movies">Movies API</a></li>
                    <li><a href="/docs">Swagger Documentation</a></li>
                    <li><a href="/redoc">ReDoc Documentation</a></li>
                    <li><a href="/health">Health Check</a></li>
                </ul>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)

@app.get("/health", tags=["monitoring"])
async def health_check():
    return {"status": "ok", "message": "Server is running", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api", tags=["monitoring"])
async def api_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "frontend": "/",
        "api_base": settings.API_V1_PREFIX,
        "endpoints": {
            "auth": f"{settings.API_V1_PREFIX}/auth",
            "movies": f"{settings.API_V1_PREFIX}/movies",
            "users": f"{settings.API_V1_PREFIX}/users",
            "reviews": f"{settings.API_V1_PREFIX}/reviews",
            "roles": f"{settings.API_V1_PREFIX}/roles",
            "picks": f"{settings.API_V1_PREFIX}/picks",
        }
    }

# ---------- Включение роутеров API ----------
app.include_router(sample_router, tags=["sample"])

# Все роутеры подключаем с префиксом API
app.include_router(movies_router, prefix=settings.API_V1_PREFIX, tags=["movies"])
app.include_router(users_router, prefix=settings.API_V1_PREFIX, tags=["users"])
app.include_router(reviews_router, prefix=settings.API_V1_PREFIX, tags=["reviews"])
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(roles_router, prefix=settings.API_V1_PREFIX, tags=["roles"])
app.include_router(movie_picks_router, prefix=settings.API_V1_PREFIX, tags=["movie-picks"])
app.include_router(movie_stats_router, prefix=settings.API_V1_PREFIX, tags=["stats"])
app.include_router(picks_router, prefix=settings.API_V1_PREFIX, tags=["picks"])
# Глобальные обработчики ошибок
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ресурс не найден"},
    )

@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )