# main_simple.py - РАБОЧАЯ УПРОЩЕННАЯ ВЕРСИЯ
import uvicorn
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер"""
    logger.info("🚀 Запуск KinoVzor API")
    try:
        from app.database.database import init_db
        init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка: {e}")
    
    yield
    
    logger.info("🛑 Остановка...")

app = FastAPI(
    title="KinoVzor API",
    version="1.0.0",
    description="Movie database application",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка статических файлов
current_dir = Path(__file__).parent
static_dir = current_dir / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Основные роуты
@app.get("/")
async def root():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>KinoVzor</title><style>
        body { font-family: Arial; margin: 20px; background: #0a0a0a; color: white; }
        h1 { color: #ff7a1a; }
        .btn { background: #ff7a1a; color: black; padding: 10px 20px; border-radius: 20px; font-weight: bold; text-decoration: none; display: inline-block; margin: 5px; }
    </style></head>
    <body>
        <h1>KinoVzor Backend is Running!</h1>
        <p><a href="/docs" class="btn">API Documentation</a>
        <a href="/health" class="btn">Health Check</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Демо-фильмы
DEMO_MOVIES = [
    {"id": 1, "title": "Интерстеллар", "year": 2014, "rating": 8.6, "genre": "Фантастика, Драма"},
    {"id": 2, "title": "Начало", "year": 2010, "rating": 8.8, "genre": "Фантастика, Боевик"},
    {"id": 3, "title": "Побег из Шоушенка", "year": 1994, "rating": 9.3, "genre": "Драма"},
]

@app.get("/api/v1/movies")
async def get_movies():
    return DEMO_MOVIES

@app.get("/api/v1/movies/{movie_id}")
async def get_movie(movie_id: int):
    movie = next((m for m in DEMO_MOVIES if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

if __name__ == "__main__":
    uvicorn.run("main_simple:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
