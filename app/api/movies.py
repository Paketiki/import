from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.movie_loader import MovieLoader

from app.schemas.movies import MovieCreate, MovieUpdate, MovieInDB, MovieWithPicks
from app.services.movies import MovieService
from app.api.dependencies import get_current_user, get_current_admin_user
from app.utils.dependencies import get_movie_service

# Убираем prefix из роутера, так как он добавляется в main.py
router = APIRouter(tags=["movies"])

@router.post("/load-from-js")
async def load_movies_from_js(
    created_by_user_id: int = 1,
    db: Session = Depends(get_db)
):
    """
    Загрузить фильмы из script.js в базу данных
    """
    loader = MovieLoader(db)
    result = loader.load_movies_to_db(created_by_user_id=created_by_user_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/movies", response_model=List[MovieWithPicks])
async def read_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    year: Optional[int] = Query(None, ge=1890, le=2030),
    genre: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    max_rating: Optional[float] = Query(None, ge=0, le=10),
    pick: Optional[str] = Query(None),
    movie_service: MovieService = Depends(get_movie_service),
):
    return await movie_service.get_movies(
        skip=skip,
        limit=limit,
        search=search,
        year=year,
        genre=genre,
        min_rating=min_rating,
        max_rating=max_rating,
        pick_name=pick
    )

@router.get("/movies/top", response_model=List[MovieWithPicks])
async def read_top_movies(
    limit: int = Query(10, ge=1, le=100),
    movie_service: MovieService = Depends(get_movie_service),
):
    return await movie_service.get_top_movies(limit)

@router.get("/movies/{movie_id}", response_model=MovieWithPicks)
async def read_movie(
    movie_id: int,
    movie_service: MovieService = Depends(get_movie_service),
):
    return await movie_service.get_movie(movie_id)

@router.post("/movies", response_model=MovieInDB)
async def create_movie(
    movie: MovieCreate,
    current_user = Depends(get_current_admin_user),
    movie_service: MovieService = Depends(get_movie_service),
):
    return await movie_service.create_movie(movie)

@router.put("/movies/{movie_id}", response_model=MovieInDB)
async def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    current_user = Depends(get_current_admin_user),
    movie_service: MovieService = Depends(get_movie_service),
):
    return await movie_service.update_movie(movie_id, movie_update)

@router.delete("/movies/{movie_id}")
async def delete_movie(
    movie_id: int,
    current_user = Depends(get_current_admin_user),
    movie_service: MovieService = Depends(get_movie_service),
):
    await movie_service.delete_movie(movie_id)
    return {"message": "Movie deleted successfully"}

@router.get("/movies/{movie_id}/stats")
async def get_movie_stats(
    movie_id: int,
    movie_service: MovieService = Depends(get_movie_service),
):
    return await movie_service.get_movie_stats(movie_id)

@router.post("/movies/{movie_id}/picks/{pick_id}")
async def add_movie_pick(
    movie_id: int,
    pick_id: int,
    current_user = Depends(get_current_admin_user),
    movie_service: MovieService = Depends(get_movie_service),
):
    await movie_service.add_pick_to_movie(movie_id, pick_id)
    return {"message": "Pick added to movie successfully"}

@router.delete("/movies/{movie_id}/picks/{pick_id}")
async def remove_movie_pick(
    movie_id: int,
    pick_id: int,
    current_user = Depends(get_current_admin_user),
    movie_service: MovieService = Depends(get_movie_service),
):
    await movie_service.remove_pick_from_movie(movie_id, pick_id)
    return {"message": "Pick removed from movie successfully"}