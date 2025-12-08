import os
from pathlib import Path
from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, SecretStr
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    # =========== БАЗОВЫЕ НАСТРОЙКИ ===========
    APP_NAME: str = Field(default="MovieApp")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)
    SECRET_KEY: SecretStr = Field(default="dev-secret-key-change-in-production")
    
    # =========== БАЗА ДАННЫХ ===========
    DATABASE_URL: str = Field(default=f"sqlite:///{BASE_DIR}/movies.db")
    
    # =========== API НАСТРОЙКИ ===========
    API_V1_PREFIX: str = Field(default="/api/v1")
    
    # ALLOWED_HOSTS как строка, которую мы преобразуем в список
    ALLOWED_HOSTS_STR: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Преобразуем строку хостов в список"""
        return [host.strip() for host in self.ALLOWED_HOSTS_STR.split(",") if host.strip()]
    
    # =========== ПОЛЬЗОВАТЕЛИ ===========
    DEFAULT_ADMIN_ID: int = Field(default=1)
    DEFAULT_ADMIN_USERNAME: str = Field(default="admin")
    DEFAULT_ADMIN_EMAIL: str = Field(default="admin@movieapp.com")
    SYSTEM_USER_ID: int = Field(default=999)
    
    # =========== ЗАГРУЗКА ДАННЫХ ===========
    LOAD_MOVIES_ON_STARTUP: bool = Field(default=False)
    MOVIES_JS_FILE_PATH: str = Field(
        default=str(BASE_DIR / "app" / "static" / "js" / "script.js")
    )
    DEFAULT_CREATED_BY_USER_ID: Optional[int] = Field(default=None)
    
    # =========== ЛОГИРОВАНИЕ ===========
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default=str(BASE_DIR / "server.log"))
    
    # =========== АУТЕНТИФИКАЦИЯ ===========
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # =========== ФАЙЛОВОЕ ХРАНИЛИЩЕ ===========
    UPLOAD_DIR: str = Field(default=str(BASE_DIR / "uploads"))
    
    # Конфигурация Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Игнорируем лишние поля
    )

# Создаем экземпляр настроек
try:
    settings = Settings()
    print(f"✅ Настройки загружены: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   База данных: {settings.DATABASE_URL}")
    print(f"   Режим отладки: {settings.DEBUG}")
except Exception as e:
    print(f"❌ Ошибка загрузки настроек: {e}")
    print("⚠️ Используются настройки по умолчанию")
    # Создаем настройки по умолчанию
    settings = Settings(
        DATABASE_URL=f"sqlite:///{BASE_DIR}/movies.db",
        DEBUG=True
    )

# Проверяем и создаем необходимые директории
def setup_directories():
    """Создает необходимые директории при старте приложения"""
    directories = [
        BASE_DIR / "uploads",
        BASE_DIR / "logs",
        Path(settings.UPLOAD_DIR),
        Path(settings.LOG_FILE).parent,
    ]
    
    for directory in directories:
        if directory and not directory.exists():
            try:
                directory.mkdir(exist_ok=True, parents=True)
                print(f"📁 Создана директория: {directory}")
            except Exception as e:
                print(f"⚠️ Не удалось создать директорию {directory}: {e}")

# Вызываем при импорте модуля
setup_directories()

# Дополнительные свойства для удобства
@property
def IS_DEVELOPMENT(self) -> bool:
    return self.DEBUG

@property
def IS_PRODUCTION(self) -> bool:
    return not self.DEBUG

# Добавляем свойства к классу Settings
Settings.IS_DEVELOPMENT = IS_DEVELOPMENT
Settings.IS_PRODUCTION = IS_PRODUCTION