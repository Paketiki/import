# main.py - УПРОЩЕННЫЙ РАБОЧИЙ ВАРИАНТ
import uvicorn
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер для управления жизненным циклом приложения"""
    # Startup логика
    logger.info("🚀 Запуск KinoVzor API")
    
    try:
        # Инициализация базы данных
        from app.database.database import init_db
        await init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка инициализации базы данных: {e}")
        logger.info("⚠️ Продолжаем без базы данных (демо-режим)")
    
    logger.info("✅ Приложение успешно запущено")
    logger.info(f"Frontend: http://localhost:8000")
    logger.info(f"API документация: http://localhost:8000/docs")
    
    yield
    
    # Shutdown логика
    logger.info("🛑 Остановка KinoVzor...")

# Создание приложения FastAPI
app = FastAPI(
    title="KinoVzor API",
    version="1.0.0",
    description="Movie database application with frontend",
    lifespan=lifespan,
)

# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Настройка статических файлов ----------
current_dir = Path(__file__).parent
static_dir = current_dir / "static"

if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ---------- Основные роуты ----------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend():
    """Главная страница фронтенда"""
    index_path = current_dir / "index.html"
    
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    
    # Простой HTML если файл не найден
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>KinoVzor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #0a0a0a; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #ff7a1a; }
            .btn { background: #ff7a1a; color: black; padding: 10px 20px; border: none; border-radius: 20px; font-weight: bold; cursor: pointer; margin: 10px 5px; text-decoration: none; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KinoVzor Backend is Running!</h1>
            <p>Frontend is loaded from index.html</p>
            <div>
                <a href="/docs" class="btn">API Documentation</a>
                <a href="/health" class="btn">Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health", tags=["monitoring"])
async def health_check():
    return {
        "status": "ok", 
        "message": "Server is running", 
        "timestamp": datetime.utcnow().isoformat(),
        "app": "KinoVzor API"
    }

@app.get("/api", tags=["monitoring"])
async def api_root():
    return {
        "app": "KinoVzor API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth_login": "/api/v1/auth/login",
            "auth_register": "/api/v1/auth/register",
            "movies": "/api/v1/movies",
        }
    }

# ---------- Временные тестовые эндпоинты ----------
# Эти эндпоинты будут работать даже если основные API модули не загружаются

from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    id: int
    title: str
    year: int
    rating: float
    genre: str
    poster_url: Optional[str] = None
    overview: Optional[str] = None
    picks: List[str] = []

class LoginData(BaseModel):
    username: str
    password: str

class RegisterData(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Демо-фильмы
DEMO_MOVIES = [
    {
        "id": 1,
        "title": "Интерстеллар",
        "year": 2014,
        "rating": 8.6,
        "genre": "Фантастика, Драма",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg",
        "overview": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планету с подходящими для человечества условиями.",
        "picks": ["hits", "classic"]
    },
    {
        "id": 2,
        "title": "Начало",
        "year": 2010,
        "rating": 8.8,
        "genre": "Фантастика, Боевик",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg",
        "overview": "Кобб — талантливый вор, лучший из лучших в опасном искусстве извлечения: он крадет ценные секреты из глубин подсознания во время сна, когда человеческий разум наиболее уязвим.",
        "picks": ["hits"]
    },
    {
        "id": 3,
        "title": "Побег из Шоушенка",
        "year": 1994,
        "rating": 9.3,
        "genre": "Драма",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg",
        "overview": "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под названием Шоушенк, он сталкивается с жестокостью и беззаконием, царящими по обе стороны решётки.",
        "picks": ["classic"]
    }
]

# Эндпоинт для входа
@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["auth"])
async def temp_login(login_data: LoginData):
    """Вход пользователя (тестовый эндпоинт)"""
    logger.info(f"Login attempt: {login_data.username}")
    return {
        "access_token": f"test_token_{login_data.username}",
        "token_type": "bearer"
    }

# Эндпоинт для регистрации
@app.post("/api/v1/auth/register", response_model=TokenResponse, tags=["auth"])
async def temp_register(register_data: RegisterData):
    """Регистрация пользователя (тестовый эндпоинт)"""
    logger.info(f"Register attempt: {register_data.username}")
    return {
        "access_token": f"test_token_{register_data.username}",
        "token_type": "bearer"
    }

# Эндпоинт для выхода
@app.post("/api/v1/auth/logout", tags=["auth"])
async def temp_logout():
    """Выход пользователя"""
    return {"message": "Successfully logged out"}

# Эндпоинт для получения фильмов
@app.get("/api/v1/movies", response_model=List[Movie], tags=["movies"])
async def get_movies():
    """Получить список фильмов (тестовый эндпоинт)"""
    return DEMO_MOVIES

# Эндпоинт для получения конкретного фильма
@app.get("/api/v1/movies/{movie_id}", response_model=Movie, tags=["movies"])
async def get_movie(movie_id: int):
    """Получить информацию о фильме (тестовый эндпоинт)"""
    movie = next((m for m in DEMO_MOVIES if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# Эндпоинт для создания фильма
@app.post("/api/v1/movies", response_model=Movie, tags=["movies"])
async def create_movie(movie: Movie):
    """Создать новый фильм (тестовый эндпоинт)"""
    logger.info(f"Creating movie: {movie.title}")
    return movie

# ---------- Пробуем подключить основные роутеры если они существуют ----------
try:
    from app.api.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1")
    logger.info("✅ Основной роутер auth подключен")
except ImportError as e:
    logger.warning(f"⚠️ Не удалось подключить основной роутер auth: {e}")
    logger.info("⚠️ Используются тестовые эндпоинты")

try:
    from app.api.movies import router as movies_router
    app.include_router(movies_router, prefix="/api/v1")
    logger.info("✅ Основной роутер movies подключен")
except ImportError as e:
    logger.warning(f"⚠️ Не удалось подключить основной роутер movies: {e}")
    logger.info("⚠️ Используются тестовые эндпоинты")

# Глобальные обработчики ошибок
from fastapi.exceptions import HTTPException

@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ресурс не найден"},
    )

@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Ошибка валидации данных"},
    )

@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )