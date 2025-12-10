# app/api/movies.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.services.movies import MovieService
from app.schemas.movies import MovieCreate, MovieUpdate, MovieInDB, MovieResponse
from app.database.database import get_db

router = APIRouter()

# 1. Сначала конкретные пути
@router.get("/test", include_in_schema=False)  # include_in_schema=False чтобы не показывать в docs
async def test_movies():
    return {"message": "Movies endpoint works"}

# 2. Потом общий путь для списка фильмов
@router.get("/", response_model=List[MovieResponse])
async def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    genre: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    pick: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить список фильмов с пагинацией и фильтрацией.
    """
    movie_service = MovieService(db)
    
    filters = {}
    if genre and genre != 'all':
        filters['genre'] = genre
    if year:
        filters['year'] = year
    if search:
        filters['search'] = search
    if rating_min:
        filters['rating_min'] = rating_min
    if rating_max:
        filters['rating_max'] = rating_max
    if pick and pick != 'all':
        filters['pick'] = pick
    
    movies = await movie_service.get_movies(
        skip=skip,
        limit=limit,
        **filters
    )
    
    return movies

# 3. Только потом путь с параметром
@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить фильм по ID.
    """
    movie_service = MovieService(db)
    
    try:
        movie = await movie_service.get_movie(movie_id)
    except AttributeError:
        movies = await movie_service.get_movies(skip=0, limit=1)
        movie = next((m for m in movies if m.id == movie_id), None)
    
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie

# ... остальные эндпоинты (POST, PUT, DELETE)

@router.put("/{movie_id}", response_model=MovieInDB)
async def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    # Убираем аутентификацию для обновления
    # current_user: User = Depends(get_current_active_user)
):
    """
    Обновить фильм.
    """
    movie_service = MovieService(db)
    
    existing_movies = await movie_service.get_movies(skip=0, limit=100)
    existing_movie = next((m for m in existing_movies if m.id == movie_id), None)
    
    if not existing_movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    try:
        updated_movie = await movie_service.update_movie(movie_id, movie)
        return updated_movie
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обновления фильма: {str(e)}"
        )

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    # Убираем аутентификацию для удаления
    # current_user: User = Depends(get_current_active_user)
):
    """
    Удалить фильм.
    """
    movie_service = MovieService(db)
    
    existing_movies = await movie_service.get_movies(skip=0, limit=100)
    existing_movie = next((m for m in existing_movies if m.id == movie_id), None)
    
    if not existing_movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    success = await movie_service.delete_movie(movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    return None