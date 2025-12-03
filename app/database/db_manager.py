from .database import engine, Base
from app.models import users, movies, reviews, picks, roles
from sqlalchemy import text

async def init_db():
    """
    Инициализация базы данных - создание таблиц
    """
    try:
        async with engine.begin() as conn:
            # Для SQLite включаем поддержку внешних ключей
            if "sqlite" in str(engine.url):
                await conn.execute(text("PRAGMA foreign_keys=ON"))

            
            # Создаем все таблицы
            await conn.run_sync(Base.metadata.create_all)
            
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        raise