#app/api/roles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.database import get_db
from app.schemas.roles import Role as RoleSchema, RoleCreate, RoleUpdate
from app.services.roles import RoleService
from app.exceptions.base import NotFoundException, ConflictException

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", response_model=List[RoleSchema])
async def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Получить список всех ролей"""
    service = RoleService(db)
    return await service.get_all_roles(skip=skip, limit=limit)

@router.get("/{role_id}", response_model=RoleSchema)
async def read_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить роль по ID"""
    service = RoleService(db)
    try:
        return await service.get_role(role_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=RoleSchema, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создать новую роль"""
    service = RoleService(db)
    try:
        return await service.create_role(role)
    except ConflictException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{role_id}", response_model=RoleSchema)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновить роль"""
    service = RoleService(db)
    try:
        return await service.update_role(role_id, role)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удалить роль"""
    service = RoleService(db)
    try:
        success = await service.delete_role(role_id)
        if not success:
            raise HTTPException(status_code=500, detail="Ошибка при удалении роли")
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))