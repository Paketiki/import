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
            # Для локальной разработки: если модель была изменена после создания БД,
            # попытаться добавить отсутствующие колонки (только для SQLite).
            if "sqlite" in str(engine.url):
                # Проверяем и добавляем column `description` в таблицу roles
                res = await conn.execute(text("PRAGMA table_info('roles')"))
                existing = [row[1] for row in res.fetchall()]
                if "description" not in existing:
                    await conn.execute(text("ALTER TABLE roles ADD COLUMN description VARCHAR(500)"))
                    print("✓ Added column roles.description")

                # Проверяем и добавляем column `creator_id` в таблицу picks
                res = await conn.execute(text("PRAGMA table_info('picks')"))
                existing = [row[1] for row in res.fetchall()]
                if "creator_id" not in existing:
                    await conn.execute(text("ALTER TABLE picks ADD COLUMN creator_id INTEGER"))
                    print("✓ Added column picks.creator_id")

        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        raise