# app/services/picks.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select

from app.models.picks import Pick
from app.schemas.picks import PickCreate, PickInDB
from app.exceptions import NotFoundError, ConflictError

class PickService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_pick(self, pick_id: int) -> Optional[PickInDB]:
        stmt = select(Pick).where(Pick.id == pick_id)
        result = await self.db.execute(stmt)
        pick = result.scalar_one_or_none()
        
        if not pick:
            raise NotFoundError(f"Подборка с ID {pick_id} не найдена")
        
        return PickInDB.from_orm(pick) if hasattr(PickInDB, 'from_orm') else PickInDB(
            id=pick.id,
            name=pick.name,
            description=pick.description,
            created_at=pick.created_at
        )
    
    async def get_pick_by_name(self, name: str) -> Optional[PickInDB]:
        stmt = select(Pick).where(Pick.name == name)
        result = await self.db.execute(stmt)
        pick = result.scalar_one_or_none()
        
        if not pick:
            raise NotFoundError(f"Подборка '{name}' не найдена")
        
        return PickInDB.from_orm(pick) if hasattr(PickInDB, 'from_orm') else PickInDB(
            id=pick.id,
            name=pick.name,
            description=pick.description,
            created_at=pick.created_at
        )
    
    async def get_picks(self, skip: int = 0, limit: int = 100) -> List[PickInDB]:
        stmt = select(Pick).offset(skip).limit(limit).order_by(Pick.name)
        result = await self.db.execute(stmt)
        picks = result.scalars().all()
        
        return [
            PickInDB.from_orm(pick) if hasattr(PickInDB, 'from_orm') else PickInDB(
                id=pick.id,
                name=pick.name,
                description=pick.description,
                created_at=pick.created_at
            )
            for pick in picks
        ]
    
    async def create_pick(self, pick_create: PickCreate, created_by: int = None) -> PickInDB:
        # Check if pick with this name already exists
        stmt = select(Pick).where(Pick.name == pick_create.name)
        result = await self.db.execute(stmt)
        existing_pick = result.scalar_one_or_none()
        
        if existing_pick:
            raise ConflictError(f"Подборка с названием '{pick_create.name}' уже существует")
        
        pick = Pick(
            name=pick_create.name,
            description=pick_create.description,
            created_by=created_by
        )
        
        self.db.add(pick)
        await self.db.commit()
        await self.db.refresh(pick)
        
        return PickInDB.from_orm(pick) if hasattr(PickInDB, 'from_orm') else PickInDB(
            id=pick.id,
            name=pick.name,
            description=pick.description,
            created_at=pick.created_at
        )
    
    async def update_pick(self, pick_id: int, pick_update: PickCreate) -> Optional[PickInDB]:
        stmt = select(Pick).where(Pick.id == pick_id)
        result = await self.db.execute(stmt)
        pick = result.scalar_one_or_none()
        
        if not pick:
            raise NotFoundError(f"Подборка с ID {pick_id} не найдена")
        
        # Check name uniqueness if name changed
        if pick_update.name != pick.name:
            name_stmt = select(Pick).where(Pick.name == pick_update.name)
            name_result = await self.db.execute(name_stmt)
            existing_pick = name_result.scalar_one_or_none()
            
            if existing_pick:
                raise ConflictError(f"Подборка с названием '{pick_update.name}' уже существует")
        
        pick.name = pick_update.name
        pick.description = pick_update.description
        
        await self.db.commit()
        await self.db.refresh(pick)
        
        return PickInDB.from_orm(pick) if hasattr(PickInDB, 'from_orm') else PickInDB(
            id=pick.id,
            name=pick.name,
            description=pick.description,
            created_at=pick.created_at
        )
    
    async def delete_pick(self, pick_id: int) -> bool:
        stmt = select(Pick).where(Pick.id == pick_id)
        result = await self.db.execute(stmt)
        pick = result.scalar_one_or_none()
        
        if not pick:
            raise NotFoundError(f"Подборка с ID {pick_id} не найдена")
        
        await self.db.delete(pick)
        await self.db.commit()
        
        return True