import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, field_validator
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Debug: Print all environment variables
print("All environment variables:")
for key, value in sorted(os.environ.items()):
    if any(keyword in key.upper() for keyword in ['CORS', 'ORIGIN', 'HOST', 'ALLOW']):
        print(f"  {key}={value}")

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).parent.parent

# Debug: Print environment variables that might affect CORS_ORIGINS
import os
cors_related_env_vars = {k: v for k, v in os.environ.items() if 'CORS' in k.upper()}
if cors_related_env_vars:
    print(f"Environment variables related to CORS: {cors_related_env_vars}")

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
    
    # =========== CORS НАСТРОЙКИ ===========
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ],
        description="List of allowed CORS origins"
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def validate_cors_origins(cls, v):
        # Handle case where CORS_ORIGINS is set to an integer or other non-list value
        if isinstance(v, int):
            # Convert integer to a default localhost URL
            return [f"http://localhost:{8000 + v}"]
        elif isinstance(v, str):
            # Split comma-separated string into list
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif not isinstance(v, list):
            # If it's neither a list, string, nor int, return default
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ]
        return v
    
    @classmethod
    def model_post_init(cls, __context):
        # Ensure CORS_ORIGINS is always a list of strings
        if hasattr(cls, 'CORS_ORIGINS'):
            if isinstance(cls.CORS_ORIGINS, int):
                cls.CORS_ORIGINS = [f"http://localhost:{8000 + cls.CORS_ORIGINS}"]
            elif isinstance(cls.CORS_ORIGINS, str):
                cls.CORS_ORIGINS = [cls.CORS_ORIGINS]
            elif not isinstance(cls.CORS_ORIGINS, list):
                cls.CORS_ORIGINS = []
        return cls
    
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
    print(f"Settings loaded: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   Database: {settings.DATABASE_URL}")
    print(f"   Debug mode: {settings.DEBUG}")
    print(f"   CORS Origins: {settings.CORS_ORIGINS}")
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Using default settings")
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
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Could not create directory {directory}: {e}")

# Вызываем при импорте модуля
setup_directories()

# Дополнительные свойства для удобства
@property
def IS_DEVELOPMENT(self) -> bool:
    return self.DEBUG

@property
def IS_PRODUCTION(self) -> bool:
    return not self.DEBUG

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

# Создаем алиасы в нижнем регистре для обратной совместимости
@property
def app_name(self) -> str:
    return self.APP_NAME

@property
def app_version(self) -> str:
    return self.APP_VERSION

@property
def debug(self) -> bool:
    return self.DEBUG

@property
def secret_key(self) -> str:
    return self.SECRET_KEY.get_secret_value() if isinstance(self.SECRET_KEY, SecretStr) else self.SECRET_KEY

@property
def database_url(self) -> str:
    return self.DATABASE_URL

@property
def api_v1_prefix(self) -> str:
    return self.API_V1_PREFIX

@property
def cors_origins(self) -> List[str]:
    return self.CORS_ORIGINS

@property
def default_admin_id(self) -> int:
    return self.DEFAULT_ADMIN_ID

@property
def default_admin_username(self) -> str:
    return self.DEFAULT_ADMIN_USERNAME

@property
def default_admin_email(self) -> str:
    return self.DEFAULT_ADMIN_EMAIL

@property
def system_user_id(self) -> int:
    return self.SYSTEM_USER_ID

@property
def load_movies_on_startup(self) -> bool:
    return self.LOAD_MOVIES_ON_STARTUP

@property
def movies_js_file_path(self) -> str:
    return self.MOVIES_JS_FILE_PATH

@property
def default_created_by_user_id(self) -> Optional[int]:
    return self.DEFAULT_CREATED_BY_USER_ID

@property
def log_level(self) -> str:
    return self.LOG_LEVEL

@property
def log_file(self) -> str:
    return self.LOG_FILE

@property
def access_token_expire_minutes(self) -> int:
    return self.ACCESS_TOKEN_EXPIRE_MINUTES

@property
def refresh_token_expire_days(self) -> int:
    return self.REFRESH_TOKEN_EXPIRE_DAYS

@property
def upload_dir(self) -> str:
    return self.UPLOAD_DIR

@property
def algorithm(self) -> str:
    return "HS256"  # Default algorithm

# Добавляем все алиасы к классу Settings
Settings.app_name = app_name
Settings.app_version = app_version
Settings.debug = debug
Settings.secret_key = secret_key
Settings.database_url = database_url
Settings.api_v1_prefix = api_v1_prefix
Settings.cors_origins = cors_origins
Settings.default_admin_id = default_admin_id
Settings.default_admin_username = default_admin_username
Settings.default_admin_email = default_admin_email
Settings.system_user_id = system_user_id
Settings.load_movies_on_startup = load_movies_on_startup
Settings.movies_js_file_path = movies_js_file_path
Settings.default_created_by_user_id = default_created_by_user_id
Settings.log_level = log_level
Settings.log_file = log_file
Settings.access_token_expire_minutes = access_token_expire_minutes
Settings.refresh_token_expire_days = refresh_token_expire_days
Settings.upload_dir = upload_dir
Settings.algorithm = algorithm