from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.repositories.picks import PickRepository
from app.schemas.picks import PickCreate, PickInDB
from app.exceptions import PickNotFoundError, DuplicateEntryError

class PickService:
    def __init__(self, db: AsyncSession):
        self.repository = PickRepository(db)
    
    async def get_pick(self, pick_id: int) -> PickInDB:
        pick = await self.repository.get(pick_id)
        if not pick:
            raise PickNotFoundError(pick_id)
        
        return PickInDB.from_orm(pick)
    
    async def get_pick_by_name(self, name: str) -> PickInDB:
        pick = await self.repository.get_by_name(name)
        if not pick:
            raise PickNotFoundError()
        
        return PickInDB.from_orm(pick)
    
    async def get_picks(self, skip: int = 0, limit: int = 100) -> List[PickInDB]:
        picks = await self.repository.get_all(skip=skip, limit=limit)
        return [PickInDB.from_orm(pick) for pick in picks]
    
    async def create_pick(self, pick_create: PickCreate) -> PickInDB:
        # Check if pick with this name already exists
        existing_pick = await self.repository.get_by_name(pick_create.name)
        if existing_pick:
            raise DuplicateEntryError(f"Pick with name '{pick_create.name}' already exists")
        
        pick = await self.repository.create(pick_create.dict())
        return PickInDB.from_orm(pick)
    
    async def update_pick(self, pick_id: int, pick_update: PickCreate) -> PickInDB:
        pick = await self.repository.get(pick_id)
        if not pick:
            raise PickNotFoundError(pick_id)
        
        updated_pick = await self.repository.update(pick_id, pick_update.dict())
        
        if not updated_pick:
            raise PickNotFoundError(pick_id)
        
        return PickInDB.from_orm(updated_pick)
    
    async def delete_pick(self, pick_id: int) -> bool:
        pick = await self.repository.get(pick_id)
        if not pick:
            raise PickNotFoundError(pick_id)
        
        return await self.repository.delete(pick_id)