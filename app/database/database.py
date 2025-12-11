from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.base import Base  # Импортируем Base из base.py
import os

# Используем SQLite базу данных movies.db
DATABASE_URL = "sqlite:///./movies.db"

# Создаем движок SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Для SQLite
    echo=False  # Показывать SQL запросы в консоли (поставьте True для отладки)
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Зависимость для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована")
