from pydantic_settings import BaseSettings
from typing import List, Optional
import json

class Settings(BaseSettings):
    # База данных
    database_url: str = "sqlite+aiosqlite:///./test.db"
    
    # JWT
    secret_key: str = "ej08rj4wg09dnviesr03wjg"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # API
    api_prefix: str = "/api/v1"
    project_name: str = "KinoVzor API"
    project_version: str = "1.0.0"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "*"]
    debug: bool = True
    
    # База данных
    db_name: str = "test.db"
    
    class Config:
        env_file = ".env"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "cors_origins":
                if raw_val.startswith("[") and raw_val.endswith("]"):
                    try:
                        return json.loads(raw_val)
                    except:
                        items = raw_val[1:-1].split(",")
                        return [item.strip().strip('"\'') for item in items if item.strip()]
                return [raw_val.strip()] if raw_val.strip() else ["*"]
            return raw_val

settings = Settings()