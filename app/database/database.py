from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import os
from app.utils.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Определяем URL базы данных
DATABASE_URL = settings.database_url

if DATABASE_URL.startswith("sqlite"):
    # Для SQLite используем специальные настройки
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
        poolclass=NullPool
    )
elif DATABASE_URL.startswith("postgresql"):
    # Для PostgreSQL
    engine = create_async_engine(DATABASE_URL, echo=settings.debug)
else:
    # По умолчанию SQLite
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
        poolclass=NullPool
    )

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()





engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии БД
def get_db():
    """
    Dependency для получения сессии базы данных.
    Используется в FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
