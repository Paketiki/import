#!/usr/bin/env python
"""
Скрипт инициализации БД — создаёт все таблицы напрямую из моделей SQLAlchemy.
Используется как обход Alembic для локальной разработки.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect
from app.database.database import engine, Base
from app.models import (
    User, Movie, Review, Role, Pick, MoviePick, MovieStat
)

async def init_db():
    """Create all tables from models."""
    print("🔄 Initializing database from models...")
    
    async with engine.begin() as conn:
        # Drop all existing tables
        print("📋 Dropping existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        print("✏️ Creating tables from models...")
        await conn.run_sync(Base.metadata.create_all)
        
    print("\n✅ Database initialization complete!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
