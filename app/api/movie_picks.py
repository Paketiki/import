# api/movie_picks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.schemas.movie_picks import MoviePick, MoviePickCreate, MoviePickUpdate, MoviePickWithDetails
from app.services.movie_picks import MoviePickService
from app.exceptions.base import NotFoundException, BadRequestException

router = APIRouter(prefix="/movie-picks", tags=["movie_picks"])

@router.get("/", response_model=List[MoviePickWithDetails])
def read_movie_picks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список связей фильмов с подборками
    """
    service = MoviePickService(db)
    return service.get_all_movie_picks_with_details(skip=skip, limit=limit)

@router.get("/{pick_id}", response_model=MoviePickWithDetails)
def read_movie_pick(
    pick_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить связь фильма с подборкой по ID
    """
    service = MoviePickService(db)
    try:
        return service.get_movie_pick_with_details(pick_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/movie/{movie_id}", response_model=List[MoviePickWithDetails])
def read_movie_picks_by_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить все подборки, в которые добавлен фильм
    """
    service = MoviePickService(db)
    return service.get_movie_picks_by_movie(movie_id)

@router.get("/pick/{pick_id}/movies", response_model=List[MoviePickWithDetails])
def read_movies_by_pick(
    pick_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить все фильмы в подборке
    """
    service = MoviePickService(db)
    return service.get_movie_picks_by_pick(pick_id)

@router.post("/", response_model=MoviePick, status_code=status.HTTP_201_CREATED)
def create_movie_pick(
    movie_pick: MoviePickCreate,
    db: Session = Depends(get_db)
):
    """
    Добавить фильм в подборку
    """
    service = MoviePickService(db)
    try:
        return service.create_movie_pick(movie_pick)
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{pick_id}", response_model=MoviePick)
def update_movie_pick(
    pick_id: int,
    movie_pick: MoviePickUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить связь фильма с подборкой
    """
    service = MoviePickService(db)
    try:
        return service.update_movie_pick(pick_id, movie_pick)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{pick_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_pick(
    pick_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить фильм из подборки
    """
    service = MoviePickService(db)
    try:
        success = service.delete_movie_pick(pick_id)
        if not success:
            raise HTTPException(status_code=500, detail="Ошибка при удалении связи")
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))