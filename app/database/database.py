from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
import logging
from typing import Generator
from contextlib import contextmanager

from app.config import settings

# Настройка логирования
logger = logging.getLogger(__name__)

# Создаем движок базы данных с оптимизациями
engine = create_engine(
    settings.DATABASE_URL, # ← исправлено: было settings.database_url
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.DEBUG,  # Используем настройку DEBUG из конфига
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite") 
    else {}
)

# Для SQLite добавляем обработчики событий
if settings.DATABASE_URL.startswith("sqlite"):
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

# Создаем фабрику сессий
SessionLocal = sessionmaker(
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

# Генератор зависимости для FastAPI
def get_db() -> Generator:
    """
    Dependency для получения сессии базы данных.
    Используется в FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
        logger.debug("Database session yielded successfully")
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")

# Контекстный менеджер для работы с БД
@contextmanager
def db_session():
    """
    Контекстный менеджер для работы с сессией БД.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        session.close()
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