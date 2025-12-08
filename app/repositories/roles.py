from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.models.roles import Role
from .base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Optional[Role]:
        return await self.get_by_field("name", name)