from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.roles import RoleRepository
from app.schemas.roles import RoleCreate, RoleUpdate, Role
from app.exceptions.base import NotFoundException, ConflictException


class RoleService:
    def __init__(self, db: AsyncSession):
        self.repository = RoleRepository(db)

    async def get_role(self, role_id: int) -> Optional[Role]:
        role = await self.repository.get(role_id)
        if not role:
            raise NotFoundException("Роль не найдена")
        return role

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        return await self.repository.get_by_name(name)

    async def get_all_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create_role(self, role: RoleCreate) -> Role:
        # Проверяем уникальность имени
        existing_role = await self.repository.get_by_name(role.name)
        if existing_role:
            raise ConflictException("Роль с таким именем уже существует")

        created = await self.repository.create(role.dict())
        return created

    async def update_role(self, role_id: int, role: RoleUpdate) -> Role:
        db_role = await self.repository.get(role_id)
        if not db_role:
            raise NotFoundException("Роль не найдена")

        # Проверяем уникальность имени, если оно изменилось
        update_data = role.dict(exclude_unset=True)
        if "name" in update_data and update_data["name"] != getattr(db_role, "name", None):
            existing_role = await self.repository.get_by_name(update_data["name"])
            if existing_role:
                raise ConflictException("Роль с таким именем уже существует")

        updated_role = await self.repository.update(role_id, update_data)
        if not updated_role:
            raise NotFoundException("Роль не найдена")

        return updated_role

    async def delete_role(self, role_id: int) -> bool:
        db_role = await self.repository.get(role_id)
        if not db_role:
            raise NotFoundException("Роль не найдена")

        return await self.repository.delete(role_id)