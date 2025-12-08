# app/config.py
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

BASE_DIR = Path(__file__).parent.parent

class Config:
    """Конфигурация приложения"""
    
    def __init__(self):
        # =========== БАЗОВЫЕ НАСТРОЙКИ ===========
        self.APP_NAME = os.getenv("APP_NAME", "MovieApp")
        self.project_name = self.APP_NAME  # Для совместимости
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.project_version = self.APP_VERSION  # Для совместимости
        self.DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes", "y")
        self.debug = self.DEBUG  # Для совместимости
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        
        # =========== БАЗА ДАННЫХ ===========
        self.DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/movies.db")
        self.database_url = self.DATABASE_URL  # Для совместимости
        
        # =========== API НАСТРОЙКИ ===========
        self.API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
        self.api_prefix = self.API_V1_PREFIX  # Для совместимости
        
        # =========== CORS И ХОСТЫ ===========
        # ALLOWED_HOSTS для CORS
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
        self.ALLOWED_HOSTS = [h.strip() for h in allowed_hosts.split(",") if h.strip()]
        
        # CORS_ORIGINS - может отличаться от ALLOWED_HOSTS
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000")
        self.CORS_ORIGINS = [h.strip() for h in cors_origins.split(",") if h.strip()]
        self.cors_origins = self.CORS_ORIGINS  # Для совместимости
        
        # =========== ПОЛЬЗОВАТЕЛИ ===========
        self.DEFAULT_ADMIN_ID = int(os.getenv("DEFAULT_ADMIN_ID", "1"))
        self.DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        self.DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@movieapp.com")
        self.SYSTEM_USER_ID = int(os.getenv("SYSTEM_USER_ID", "999"))
        
        # =========== ЗАГРУЗКА ДАННЫХ ===========
        self.LOAD_MOVIES_ON_STARTUP = os.getenv("LOAD_MOVIES_ON_STARTUP", "False").lower() in ("true", "1", "yes", "y")
        self.MOVIES_JS_FILE_PATH = os.getenv("MOVIES_JS_FILE_PATH", str(BASE_DIR / "app" / "static" / "js" / "script.js"))
        
        default_user_id = os.getenv("DEFAULT_CREATED_BY_USER_ID")
        self.DEFAULT_CREATED_BY_USER_ID = int(default_user_id) if default_user_id else None
        
        # =========== ЛОГИРОВАНИЕ ===========
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "server.log"))
        self.log_level = self.LOG_LEVEL  # Для совместимости
        self.log_file = self.LOG_FILE  # Для совместимости
        
        # =========== АУТЕНТИФИКАЦИЯ ===========
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.access_token_expire_minutes = self.ACCESS_TOKEN_EXPIRE_MINUTES  # Для совместимости
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.refresh_token_expire_days = self.REFRESH_TOKEN_EXPIRE_DAYS  # Для совместимости
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.algorithm = self.ALGORITHM  # Для совместимости
        
        # =========== ФАЙЛОВОЕ ХРАНИЛИЩЕ ===========
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
        self.upload_dir = self.UPLOAD_DIR  # Для совместимости
        
        # =========== СЕРВЕР ===========
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        
        # Создаем директории
        self._create_directories()
        
        # Выводим информацию о настройках
        self._print_summary()
    
    def _create_directories(self):
        """Создает необходимые директории"""
        dirs_to_create = [
            BASE_DIR / "uploads",
            BASE_DIR / "logs",
            Path(self.UPLOAD_DIR),
            Path(self.LOG_FILE).parent,
        ]
        
        for directory in dirs_to_create:
            if directory and not directory.exists():
                try:
                    directory.mkdir(exist_ok=True, parents=True)
                except Exception as e:
                    print(f"⚠️ Не удалось создать директорию {directory}: {e}")
    
    def _print_summary(self):
        """Выводит краткую информацию о настройках"""
        print("=" * 50)
        print("НАСТРОКИ ПРИЛОЖЕНИЯ")
        print("=" * 50)
        print(f"Приложение: {self.APP_NAME} v{self.APP_VERSION}")
        print(f"Режим: {'Разработка' if self.DEBUG else 'Продакшен'}")
        print(f"База данных: {self.DATABASE_URL}")
        print(f"API префикс: {self.API_V1_PREFIX}")
        print(f"Хост:порт: {self.HOST}:{self.PORT}")
        print(f"CORS origins: {', '.join(self.CORS_ORIGINS[:3])}{'...' if len(self.CORS_ORIGINS) > 3 else ''}")
        print(f"Автозагрузка фильмов: {'Да' if self.LOAD_MOVIES_ON_STARTUP else 'Нет'}")
        print("=" * 50)

# Создаем экземпляр настроек
settings = Config()
