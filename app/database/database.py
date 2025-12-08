from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool
import logging
from typing import Generator, AsyncGenerator
from contextlib import asynccontextmanager

from app.config import settings

# Настройка логирования
logger = logging.getLogger(__name__)

# Создаем асинхронный движок базы данных
engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///"),
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)


# Для SQLite добавляем обработчики событий
if settings.DATABASE_URL.startswith("sqlite"):
    
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
# Создаем фабрику асинхронных сессий
SessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


# Базовый класс для моделей
Base = declarative_base()


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Только для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Асинхронный генератор зависимости для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии базы данных.
    Используется в FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
        logger.debug("Database session yielded successfully")
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()
        logger.debug("Database session closed")

# Асинхронный контекстный менеджер для работы с БД
@asynccontextmanager
async def db_session():
    """
    Асинхронный контекстный менеджер для работы с сессией БД.
    """
    session = SessionLocal()
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
def check_connection():
    """Проверка подключения к базе данных"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection: OK")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# Инициализация базы данных
def init_db():
    """
    Инициализация базы данных - создание всех таблиц.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False

# Экспортируем всё необходимое
__all__ = [
    'engine',
    'SessionLocal',
    'SessionScoped',
    'Base',
    'get_db',
    'db_session',
    'check_connection',
    'init_db',
]