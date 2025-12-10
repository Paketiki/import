#app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional

from app.services.users import UserService
from app.services.auth import AuthService
from app.schemas.auth import Token, TokenData
from app.schemas.users import UserCreate, UserInDB
from app.utils.config import settings
from app.utils.dependencies import get_user_service, get_auth_service
# Убираем зависимости, так как теперь нет аутентификации для /me
# from app.api.dependencies import get_current_user
# from app.models.users import User as UserModel

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserInDB)
async def register(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_user(user_create)

@router.post("/logout")
async def logout():
    """
    Выход пользователя
    """
    # Так как нет аутентификации, просто возвращаем сообщение
    return {"message": "Successfully logged out"}

# Убираем /me, так как нет аутентификации
# @router.get("/me")
# async def read_users_me(
#     current_user: UserModel = Depends(get_current_user)
# ):
#     """
#     Получить информацию о текущем пользователе
#     """
#     return current_user

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Обновить access токен
    """
    try:
        new_access_token = auth_service.refresh_access_token(refresh_token)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    