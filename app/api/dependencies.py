# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import JWTError, jwt

from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.users import UserService
from app.schemas.users import UserInDB
from app.schemas.auth import TokenData
from app.utils.config import settings

# Делаем авторизацию необязательной
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserInDB]:
    if not token:
        return None
    
    try:
        # Декодируем токен
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        
        token_data = TokenData(username=username)
    except JWTError:
        return None
    
    # Получаем пользователя из базы данных
    user_service = UserService(db)
    user = await user_service.get_user_by_username(token_data.username)
    return user

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    # Всегда возвращаем пользователя или None
    return current_user

async def get_current_admin_user(
    current_user: UserInDB = Depends(get_current_user),
) -> Optional[UserInDB]:
    if current_user and any(role.name == "Администратор" for role in current_user.roles):
        return current_user
    return None