# app/repositories/picks.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.picks import Pick  # Исправленный импорт
from app.repositories.base import BaseRepository

class PickRepository(BaseRepository[Pick]):
    def __init__(self, db: AsyncSession):
        super().__init__(Pick, db)
    
    async def get_by_name(self, name: str) -> Optional[Pick]:
        result = await self.db.execute(
            select(Pick).where(Pick.name == name)
        )
        return result.scalar_one_or_none()