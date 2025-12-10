# app/api/movies.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models import Movie, Pick, MoviePick
from app.models.users import User
from app.schemas import MovieResponse, MovieDetailResponse, MovieCreate
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MovieResponse])
async def get_movies(
    genre: Optional[str] = Query(None, description="Фильтр по жанру"),
    rating_min: Optional[float] = Query(None, description="Минимальный рейтинг"),
    pick: Optional[str] = Query(None, description="Фильтр по подборке"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    db: Session = Depends(get_db)
):
    """Получить список фильмов с фильтрами"""
    query = db.query(Movie)
    
    if genre and genre != "all":
        query = query.filter(Movie.genre.contains(genre))
    
    if rating_min:
        query = query.filter(Movie.rating >= rating_min)
    
    if pick and pick != "all":
        # Фильтруем по подборкам
        pick_obj = db.query(Pick).filter(Pick.slug == pick).first()
        if pick_obj:
            query = query.join(MoviePick).filter(MoviePick.pick_id == pick_obj.id)
    
    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    
    movies = query.all()
    return movies

@router.get("/{movie_id}", response_model=MovieDetailResponse)
async def get_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о фильме"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    # Получаем подборки фильма
    picks_query = db.query(Pick).join(MoviePick).filter(MoviePick.movie_id == movie_id)
    picks = picks_query.all()
    
    # Создаем словарь с данными фильма и подборками
    movie_data = {
        **movie.__dict__,
        "picks": [pick.slug for pick in picks],
        "reviews_count": 0  # Можно добавить логику подсчета рецензий
    }
    
    return MovieDetailResponse(**movie_data)

@router.post("/", response_model=MovieResponse)
async def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый фильм (только для администраторов)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверяем существование фильма с таким названием
    existing_movie = db.query(Movie).filter(Movie.title == movie.title).first()
    if existing_movie:
        raise HTTPException(status_code=400, detail="Фильм с таким названием уже существует")
    
    db_movie = Movie(
        title=movie.title,
        overview=movie.overview,
        year=movie.year,
        genre=movie.genre,
        rating=movie.rating,
        poster_url=movie.poster_url,
        created_by=current_user.id
    )
    
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    
    # Добавляем подборки
    if movie.picks:
        for pick_slug in movie.picks:
            pick = db.query(Pick).filter(Pick.slug == pick_slug).first()
            if pick:
                movie_pick = MoviePick(movie_id=db_movie.id, pick_id=pick.id)
                db.add(movie_pick)
        
        db.commit()
    
    return db_movie

@router.get("/genres/list")
async def get_genres_list(db: Session = Depends(get_db)):
    """Получить список всех жанров"""
    movies = db.query(Movie).all()
    genres = set()
    
    for movie in movies:
        if movie.genre:
            # Разделяем жанры по запятым
            movie_genres = [g.strip() for g in movie.genre.split(",")]
            for genre in movie_genres:
                if genre:
                    genres.add(genre)
    
    return {"genres": sorted(list(genres))}