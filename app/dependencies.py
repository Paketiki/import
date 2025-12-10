# app/dependencies.py
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_db

# Асинхронная зависимость для получения сессии БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_db():
        yield session

# Синхронная зависимость (если нужна)
def get_sync_db():
    from app.database.database import get_db as sync_get_db
    return sync_get_db()