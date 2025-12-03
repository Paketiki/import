from typing import Generic, TypeVar, Optional, List, Dict, Any
from app.repositories.base import BaseRepository
from app.exceptions.base import NotFoundError

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
OutputSchemaType = TypeVar("OutputSchemaType")

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, OutputSchemaType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository
    
    async def get(self, id: Any) -> Optional[OutputSchemaType]:
        entity = await self.repository.get(id)
        if not entity:
            return None
        return OutputSchemaType.from_orm(entity)
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[OutputSchemaType]:
        entities = await self.repository.get_all(skip=skip, limit=limit, filters=filters)
        return [OutputSchemaType.from_orm(entity) for entity in entities]
    
    async def create(self, obj_in: CreateSchemaType) -> OutputSchemaType:
        obj_dict = obj_in.dict()
        entity = await self.repository.create(obj_dict)
        return OutputSchemaType.from_orm(entity)
    
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> Optional[OutputSchemaType]:
        obj_dict = obj_in.dict(exclude_unset=True)
        entity = await self.repository.update(id, obj_dict)
        if entity:
            return OutputSchemaType.from_orm(entity)
        return None
    
    async def delete(self, id: Any) -> bool:
        return await self.repository.delete(id)