# app/utils/config.py
import os
from typing import List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # Параметры приложения
    APP_NAME: str = "MovieApp"
    DEBUG: bool = True
    
    # Параметры базы данных
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/movies.db"
    
    # JWT настройки
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS настройки
    CORS_ORIGINS: List[str] = ["*"]
    
    # Параметры хоста
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()