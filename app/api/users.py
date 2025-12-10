# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import User, UserCreate, UserUpdate, UserResponse
from app.schemas.movies import MovieResponse
from app.services.users import UserService
from app.services.movies import MovieService
from app.database.database import get_db
from app.api.dependencies import get_current_user, get_current_active_user
from app.models.users import User as UserModel

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Получить информацию о текущем пользователе
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Обновить информацию о текущем пользователе
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    updated_user = await UserService(db).update_user(current_user.id, user_update)
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Удалить текущего пользователя
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    await UserService(db).delete_user(current_user.id)
    return None

# ===================== ИЗБРАННОЕ =====================

@router.get("/me/favorites", response_model=List[MovieResponse])
async def get_user_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Получить избранные фильмы текущего пользователя
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    favorites = await MovieService(db).get_user_favorites(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return favorites

@router.post("/me/favorites", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    favorite_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Добавить фильм в избранное
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    movie_id = favorite_data.get("movie_id")
    if not movie_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не указан movie_id"
        )
    
    # Проверяем, существует ли фильм
    movie = await MovieService(db).get_movie(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )
    
    # Проверяем, не добавлен ли уже фильм в избранное
    existing_favorite = await MovieService(db).get_user_favorite(current_user.id, movie_id)
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Фильм уже добавлен в избранное"
        )
    
    # Добавляем в избранное
    await MovieService(db).add_to_favorites(current_user.id, movie_id)
    
    return {"message": "Фильм добавлен в избранное", "movie_id": movie_id}

# app/api/users.py
# Исправьте этот эндпоинт:

@router.delete("/me/favorites/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)  # <-- ИСПРАВЛЕНО
async def remove_from_favorites(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Удалить фильм из избранного
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    # Проверяем, существует ли фильм в избранном
    favorite = await MovieService(db).get_user_favorite(current_user.id, movie_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден в избранном"
        )
    
    # Удаляем из избранного
    await MovieService(db).remove_from_favorites(current_user.id, movie_id)
    
    return None

@router.get("/me/favorites/{movie_id}", response_model=dict)
async def check_favorite(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Проверить, добавлен ли фильм в избранное
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    favorite = await MovieService(db).get_user_favorite(current_user.id, movie_id)
    return {"is_favorite": favorite is not None, "movie_id": movie_id}

# ===================== АДМИНИСТРИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ =====================

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    # Убираем обязательную аутентификацию
    # current_user: UserModel = Depends(get_current_active_user)
):
    """
    Получить список пользователей
    """
    users = await UserService(db).get_users(skip=skip, limit=limit, search=search, role_name=role)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # Убираем обязательную аутентификацию
    # current_user: UserModel = Depends(get_current_active_user)
):
    """
    Получить информацию о пользователе
    """
    user = await UserService(db).get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    # Убираем обязательную аутентификацию
    # current_user: UserModel = Depends(get_current_active_user)
):
    """
    Обновить информацию о пользователе
    """
    updated_user = await UserService(db).update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # Убираем обязательную аутентификацию
    # current_user: UserModel = Depends(get_current_active_user)
):
    """
    Удалить пользователя
    """
    deleted = await UserService(db).delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return None