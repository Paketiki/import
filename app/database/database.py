# app/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Используем SQLite базу данных movies.db
DATABASE_URL = "sqlite:///./movies.db"

# Создаем движок SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Для SQLite
    echo=True  # Показывать SQL запросы в консоли
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

# Добавьте эту функцию, если нужна init_db
def init_db():
    """Инициализация базы данных"""
    from .base import Base
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована")