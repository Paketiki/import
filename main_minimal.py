# main_minimal.py - минимальная рабочая версия
import uvicorn
import sys
import os
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

app = FastAPI(title="KinoVzor API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Основные роуты
@app.get("/")
async def root():
    return {"message": "KinoVzor API работает!"}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Демо-фильмы
DEMO_MOVIES = [
    {"id": 1, "title": "Интерстеллар", "year": 2014, "rating": 8.6},
    {"id": 2, "title": "Начало", "year": 2010, "rating": 8.8},
    {"id": 3, "title": "Побег из Шоушенка", "year": 1994, "rating": 9.3},
]

@app.get("/api/v1/movies")
async def get_movies():
    return DEMO_MOVIES

if __name__ == "__main__":
    uvicorn.run("main_minimal:app", host="127.0.0.1", port=8000, reload=True)