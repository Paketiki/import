from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.database.database import Base 
from app.schemas.users import UserInDB, UserUpdate
from app.services.users import UserService
from app.api.dependencies import get_current_user, get_current_admin_user
from app.utils.dependencies import get_user_service

# Убираем prefix из роутера
router = APIRouter(tags=["users"])

@router.get("/users", response_model=List[UserInDB])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    current_user: UserInDB = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_users(skip=skip, limit=limit, role=role)

@router.get("/users/me", response_model=UserInDB)
async def read_current_user(
    current_user: UserInDB = Depends(get_current_user),
):
    return current_user

@router.get("/users/{username}", response_model=UserInDB)
async def read_user(
    username: str,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    # Users can only view their own profile unless they're admin
    if username != current_user.username and current_user.role.value != "admin":
        from app.exceptions import InsufficientPermissionsError
        raise InsufficientPermissionsError()
    
    return await user_service.get_user(username)

@router.put("/users/{username}", response_model=UserInDB)
async def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    # Users can only update their own profile unless they're admin
    if username != current_user.username and current_user.role.value != "admin":
        from app.exceptions import InsufficientPermissionsError
        raise InsufficientPermissionsError()
    
    return await user_service.update_user(username, user_update)

@router.delete("/users/{username}")
async def delete_user(
    username: str,
    current_user: UserInDB = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(username)
    return {"message": "User deleted successfully"}