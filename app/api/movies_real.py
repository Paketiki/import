# app/api/movies_real.py - Реальный API для фильмов из БД
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.database.database import get_db
from app.models.movies import Movie
from app.models.picks import Pick
from app.models.movie_picks import MoviePick

router = APIRouter()

# Схемы Pydantic
class MovieResponse(BaseModel):
    id: int
    title: str
    year: int
    rating: float
    genre: str
    poster_url: Optional[str] = None
    overview: Optional[str] = None
    picks: List[str] = []
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[MovieResponse])
def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    genre: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    pick: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Получить список фильмов из БД с пагинацией и фильтрацией.
    """
    query = db.query(Movie)
    
    # Применяем фильтры
    if genre and genre != 'all':
        query = query.filter(Movie.genre.contains(genre))
    
    if year:
        query = query.filter(Movie.year == year)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            Movie.title.ilike(search_term),
            Movie.overview.ilike(search_term),
            Movie.genre.ilike(search_term)
        ))
    
    if rating_min:
        query = query.filter(Movie.rating >= rating_min)
    
    if rating_max:
        query = query.filter(Movie.rating <= rating_max)
    
    # Фильтр по подборкам
    if pick and pick != 'all':
        # Ищем ID подборки по slug
        pick_record = db.query(Pick).filter(Pick.slug == pick).first()
        if pick_record:
            query = query.join(Movie.picks).filter(Pick.id == pick_record.id)
    
    # Применяем пагинацию
    movies = query.offset(skip).limit(limit).all()
    
    # Преобразуем в ответ
    result = []
    for movie in movies:
        # Получаем подборки для фильма
        picks = []
        for movie_pick in movie.picks:
            picks.append(movie_pick.slug)
        
        result.append(MovieResponse(
            id=movie.id,
            title=movie.title,
            year=movie.year,
            rating=movie.rating,
            genre=movie.genre,
            poster_url=movie.poster_url,
            overview=movie.overview,
            picks=picks
        ))
    
    return result

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Получить фильм по ID из БД.
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    # Получаем подборки для фильма
    picks = []
    for pick in movie.picks:
        picks.append(pick.slug)
    
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        year=movie.year,
        rating=movie.rating,
        genre=movie.genre,
        poster_url=movie.poster_url,
        overview=movie.overview,
        picks=picks
    )

# Эндпоинты для создания, обновления и удаления фильмов
class MovieCreate(BaseModel):
    title: str
    year: int
    genre: str
    rating: float
    poster_url: Optional[str] = None
    overview: Optional[str] = None
    picks: List[str] = []

@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(movie_data: MovieCreate, db: Session = Depends(get_db)):
    """
    Создать новый фильм в БД.
    """
    # Создаем фильм
    movie = Movie(
        title=movie_data.title,
        year=movie_data.year,
        genre=movie_data.genre,
        rating=movie_data.rating,
        poster_url=movie_data.poster_url,
        overview=movie_data.overview,
        created_by=1  # ID администратора (по умолчанию)
    )
    
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    # Добавляем подборки
    for pick_slug in movie_data.picks:
        pick = db.query(Pick).filter(Pick.slug == pick_slug).first()
        if pick:
            movie_pick = MoviePick(movie_id=movie.id, pick_id=pick.id)
            db.add(movie_pick)
    
    db.commit()
    db.refresh(movie)
    
    # Возвращаем фильм с подборками
    picks = [pick.slug for pick in movie.picks]
    
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        year=movie.year,
        rating=movie.rating,
        genre=movie.genre,
        poster_url=movie.poster_url,
        overview=movie.overview,
        picks=picks
    )