from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.picks import Pick
from .base import BaseRepository

class PickRepository(BaseRepository[Pick]):
    def __init__(self, db: AsyncSession):
        super().__init__(Pick, db)
    
    async def get_by_name(self, name: str) -> Optional[Pick]:
        return await self.get_by_field("name", name)