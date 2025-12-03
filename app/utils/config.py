from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Существующие настройки (берем из .env)
    secret_key: str = "ej08rj4wg09dnviesr03wjg"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    db_name: str = "test.db"
    
    # Новые настройки для PostgreSQL/SQLite
    database_url: str = "sqlite+aiosqlite:///./test.db"  # По умолчанию SQLite для совместимости
    
    # API настройки
    api_prefix: str = "/api/v1"
    project_name: str = "KinoVzor API"
    project_version: str = "1.0.0"
    cors_origins: List[str] = ["*"]
    debug: bool = True
    
    class Config:
        env_file = ".env"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "cors_origins":
                # Преобразуем строку в список
                if raw_val.startswith("[") and raw_val.endswith("]"):
                    # Убираем скобки и кавычки, разделяем по запятым
                    items = raw_val[1:-1].split(",")
                    return [item.strip().strip('"\'') for item in items if item.strip()]
                return raw_val.split(",") if raw_val else ["*"]
            return raw_val

settings = Settings()