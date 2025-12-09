# app/database/db_manager.py
import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator

# Добавляем корень проекта в PYTHONPATH для корректных импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .database import engine, Base, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

async def init_db():
    """Публичная функция для инициализации БД"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы базы данных созданы")
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False

async def create_tables():
    """Создание таблиц в БД"""
    return await init_db()

async def drop_tables():
    """Удаление всех таблиц (только для разработки!)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("⚠️ Все таблицы удалены")
        return True
    except Exception as e:
        print(f"❌ Ошибка при удалении таблиц: {e}")
        return False

async def reset_db():
    """Полный сброс базы данных (удаление и создание таблиц)"""
    await drop_tables()
    await create_tables()

# ДОБАВЛЯЕМ ЭТУ ФУНКЦИЮ
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный генератор для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный контекстный менеджер для работы с сессией БД"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

def get_sync_session():
    """Получение сессии для синхронных операций (не рекомендуется)"""
    raise DeprecationWarning("Используйте асинхронные сессии. Вызовите get_session() с await или используйте асинхронный контекст")

# Если файл запускается напрямую
if __name__ == "__main__":
    async def main():
        import argparse
        
        parser = argparse.ArgumentParser(description="Управление базой данных")
        parser.add_argument("--create", action="store_true", help="Создать таблицы")
        parser.add_argument("--drop", action="store_true", help="Удалить таблицы")
        parser.add_argument("--reset", action="store_true", help="Сбросить базу данных")
        parser.add_argument("--check", action="store_true", help="Проверить соединение")
        
        args = parser.parse_args()
        
        if args.create:
            await create_tables()
        elif args.drop:
            confirm = input("Вы уверены, что хотите удалить все таблицы? (y/N): ")
            if confirm.lower() == 'y':
                await drop_tables()
        elif args.reset:
            confirm = input("Вы уверены, что хотите сбросить базу данных? (y/N): ")
            if confirm.lower() == 'y':
                await reset_db()
        elif args.check:
            try:
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")
                print("✅ Соединение с БД установлено")
            except Exception as e:
                print(f"❌ Ошибка соединения с БД: {e}")
        else:
            print("Доступные команды:")
            print("  --create    Создать таблицы")
            print("  --drop      Удалить таблицы")
            print("  --reset     Сбросить базу данных")
            print("  --check     Проверить соединение")
    
    asyncio.run(main())