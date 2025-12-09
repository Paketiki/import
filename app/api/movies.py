# app/api/movies.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.services.movies import MovieService
from app.schemas.movies import MovieCreate, MovieUpdate, MovieInDB
from app.utils.dependencies import get_movie_service  # или создайте эту зависимость

router = APIRouter()

@router.get("/movies", response_model=List[MovieInDB])
async def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    genre: Optional[str] = None,
    year: Optional[int] = None,
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Получить список фильмов с пагинацией и фильтрацией.
    """
    filters = {}
    if genre:
        filters['genre'] = genre
    if year:
        filters['year'] = year
    
    movies = await movie_service.get_movies(
        skip=skip, 
        limit=limit, 
        **filters
    )
    return movies

@router.get("/movies/{movie_id}", response_model=MovieInDB)
async def get_movie(
    movie_id: int,
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Получить фильм по ID.
    """
    movie = await movie_service.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.post("/movies", response_model=MovieInDB)
async def create_movie(
    movie: MovieCreate,
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Создать новый фильм.
    """
    return await movie_service.create_movie(movie)

@router.put("/movies/{movie_id}", response_model=MovieInDB)
async def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Обновить фильм.
    """
    updated_movie = await movie_service.update_movie(movie_id, movie)
    if not updated_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated_movie

@router.delete("/movies/{movie_id}")
async def delete_movie(
    movie_id: int,
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Удалить фильм.
    """
    success = await movie_service.delete_movie(movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}