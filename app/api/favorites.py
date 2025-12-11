from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models import Movie, User
from app.schemas import MovieResponse
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[MovieResponse])
async def get_user_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить избранные фильмы текущего пользователя"""
    # Получаем избранные фильмы текущего пользователя
    favorites = current_user.favorite_movies if hasattr(current_user, 'favorite_movies') else []
    return favorites


@router.post("/{movie_id}")
async def add_to_favorites(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Надобавить фильм в избранное"""
    # Проверяем осуществляется ли такой фильм
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    # Проверяем, не добавлен ли же фильм
    if hasattr(current_user, 'favorite_movies'):
        if movie in current_user.favorite_movies:
            raise HTTPException(status_code=400, detail="Фильм уже в избранном")
        current_user.favorite_movies.append(movie)
    
    db.commit()
    return {"message": "Фильм добавлен в избранное"}


@router.delete("/{movie_id}")
async def remove_from_favorites(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить фильм из избранного"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    if hasattr(current_user, 'favorite_movies'):
        if movie not in current_user.favorite_movies:
            raise HTTPException(status_code=400, detail="Фильм не в избранном")
        current_user.favorite_movies.remove(movie)
    
    db.commit()
    return {"message": "Фильм удален из избранного"}


@router.get("/{movie_id}/is-favorite")
async def is_movie_favorite(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Проверить, находится ли фильм в избранном"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    is_favorite = False
    if hasattr(current_user, 'favorite_movies'):
        is_favorite = movie in current_user.favorite_movies
    
    return {"is_favorite": is_favorite}
