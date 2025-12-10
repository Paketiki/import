from sqlalchemy import event, text
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from app.config import settings
from sqlalchemy import event, text
from app.config import settings
from .base import Base

# Настройка логирования
logger = logging.getLogger(__name__)


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Только для SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Создаем асинхронный движок базы данных
DATABASE_URL = getattr(settings, "DATABASE_URL", "sqlite:///./movies.db")
DEBUG = getattr(settings, "DEBUG", False)



# Преобразуем URL для асинхронного SQLite
async_database_url = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    async_database_url,
    echo=DEBUG,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Пересоздание соединений каждые 3600 секунд
    future=True
)

# Для SQLite добавляем обработчики событий
# ВНИМАНИЕ: Для асинхронного SQLite через aiosqlite обработчики событий
# должны применяться к синхронному движку
if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

# Создаем фабрику асинхронных сессий с использованием async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()


# Асинхронный генератор зависимости для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии БД в FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise
        finally:
            await session.close()


# Асинхронный контекстный менеджер для работы с БД
@asynccontextmanager
async def db_session():
    """
    Асинхронный контекстный менеджер для работы с сессией БД.
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        await session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        await session.close()
        logger.debug("Session closed")


# Проверка подключения к БД
async def check_connection():
    """Асинхронная проверка подключения к базе данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection: OK")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# Инициализация базы данных (асинхронная)
async def init_db():
    """
    Асинхронная инициализация базы данных - создание всех таблиц.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False


# Синхронная инициализация для db_manager
def sync_init_db():
    """
    Синхронная инициализация базы данных.
    Используется db_manager.py
    """
    import asyncio
    return asyncio.run(init_db())


# Закрытие соединений
async def close_connections():
    """
    Закрытие всех соединений с базой данных.
    """
    await engine.dispose()
    logger.info("Database connections closed")


# Экспортируем всё необходимое
__all__ = [
    'engine',
    'AsyncSessionLocal',
    'Base',
    'get_db',
    'db_session',
    'check_connection',
    'init_db',
    'sync_init_db',
    'close_connections',
]