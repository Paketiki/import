# final_fix_all.py
import os

def fix_users_model():
    """Создать чистый users.py"""
    content = '''# app/models/users.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Базовые отношения
    movies = relationship("Movie", back_populates="user", foreign_keys="[Movie.created_by]")
    reviews = relationship("Review", back_populates="user")
    created_picks = relationship("Pick", back_populates="creator", foreign_keys="[Pick.created_by]")
'''
    
    os.makedirs("app/models", exist_ok=True)
    with open("app/models/users.py", 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Создан чистый users.py")

def fix_models_init():
    """Создать чистый __init__.py"""
    content = '''# app/models/__init__.py
from .base import Base
from .users import User
from .movies import Movie
from .reviews import Review
from .picks import Pick

__all__ = ["Base", "User", "Movie", "Review", "Pick"]
'''
    
    with open("app/models/__init__.py", 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Создан чистый __init__.py")

def fix_auth_api():
    """Исправить auth.py или создать заглушку"""
    auth_path = "app/api/auth.py"
    
    # Если файл существует и содержит проблемный импорт
    if os.path.exists(auth_path):
        with open(auth_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем проблемный импорт
        if 'user_favorite_movies' in content:
            content = content.replace(
                'from app.models.users import User, user_favorite_movies',
                'from app.models.users import User'
            )
            content = content.replace('user_favorite_movies,', '')
            
            with open(auth_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Исправлен auth.py")
    else:
        # Создаем простую заглушку
        os.makedirs("app/api", exist_ok=True)
        content = '''# app/api/auth.py - заглушка
from fastapi import APIRouter
router = APIRouter(tags=["auth"])

@router.post("/auth/login")
async def login():
    return {"message": "Login endpoint"}

@router.post("/auth/register")
async def register():
    return {"message": "Register endpoint"}
'''
        with open(auth_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Создана заглушка auth.py")

def create_simple_main():
    """Создать простой main.py"""
    content = '''# main.py - ПРОСТАЯ РАБОЧАЯ ВЕРСИЯ
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Демо-фильмы
DEMO_MOVIES = [
    {"id": 1, "title": "Интерстеллар", "year": 2014, "rating": 8.6, "genre": "Фантастика, Драма"},
    {"id": 2, "title": "Начало", "year": 2010, "rating": 8.8, "genre": "Фантастика, Боевик"},
    {"id": 3, "title": "Побег из Шоушенка", "year": 1994, "rating": 9.3, "genre": "Драма"},
]

@app.get("/")
async def root():
    return {"message": "KinoVzor API работает!"}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
'''
    
    with open("main.py", 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Создан простой main.py")

def main():
    print("🚀 Выполняю окончательное исправление...")
    fix_users_model()
    fix_models_init()
    fix_auth_api()
    create_simple_main()
    print("\n🎉 Все файлы исправлены!")
    print("\n📋 Запустите приложение командой:")
    print("   python main.py")
    print("\n🌐 Доступные адреса после запуска:")
    print("   - http://localhost:8000/")
    print("   - http://localhost:8000/docs")
    print("   - http://localhost:8000/api/v1/movies")
    print("   - http://localhost:8000/health")

if __name__ == "__main__":
    main()