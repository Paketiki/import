from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, and_, or_
from typing import List, Optional
from app.models.users import User
from .base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.get_by_field("username", username)
    
    async def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"role": role}
        )
    
    async def update_password(self, username: str, hashed_password: str) -> Optional[User]:
        return await self.update(username, {"password": hashed_password})