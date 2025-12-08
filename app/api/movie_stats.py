# api/movie_stats.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.schemas.movie_stats import MovieStat, MovieStatCreate, MovieStatUpdate, MovieStatWithMovie
from app.services.movie_stats import MovieStatService
from app.exceptions.base import NotFoundException, ConflictException

router = APIRouter(prefix="/movie-stats", tags=["movie_stats"])

@router.get("/", response_model=List[MovieStatWithMovie])
def read_movie_stats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список статистики фильмов
    """
    service = MovieStatService(db)
    return service.get_all_movie_stats_with_movies(skip=skip, limit=limit)

@router.get("/{stat_id}", response_model=MovieStatWithMovie)
def read_movie_stat(
    stat_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить статистику фильма по ID
    """
    service = MovieStatService(db)
    try:
        stat = service.get_movie_stat(stat_id)
        stat_dict = {**stat.__dict__}
        if hasattr(stat, 'movie'):
            stat_dict['movie_title'] = stat.movie.title
            stat_dict['movie_release_year'] = stat.movie.release_year
        return MovieStatWithMovie(**stat_dict)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/movie/{movie_id}", response_model=MovieStatWithMovie)
def read_movie_stat_by_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить статистику по ID фильма
    """
    service = MovieStatService(db)
    try:
        stat = service.get_movie_stat_by_movie(movie_id)
        stat_dict = {**stat.__dict__}
        if hasattr(stat, 'movie'):
            stat_dict['movie_title'] = stat.movie.title
            stat_dict['movie_release_year'] = stat.movie.release_year
        return MovieStatWithMovie(**stat_dict)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=MovieStat, status_code=status.HTTP_201_CREATED)
def create_movie_stat(
    stat: MovieStatCreate,
    db: Session = Depends(get_db)
):
    """
    Создать новую статистику для фильма
    """
    service = MovieStatService(db)
    try:
        return service.create_movie_stat(stat)
    except ConflictException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{stat_id}", response_model=MovieStat)
def update_movie_stat(
    stat_id: int,
    stat: MovieStatUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить статистику фильма
    """
    service = MovieStatService(db)
    try:
        return service.update_movie_stat(stat_id, stat)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/movie/{movie_id}/increment-views", response_model=MovieStat)
def increment_movie_views(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Увеличить счетчик просмотров фильма
    """
    service = MovieStatService(db)
    try:
        return service.increment_views(movie_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{stat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_stat(
    stat_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить статистику фильма
    """
    service = MovieStatService(db)
    try:
        success = service.delete_movie_stat(stat_id)
        if not success:
            raise HTTPException(status_code=500, detail="Ошибка при удалении статистики")
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))