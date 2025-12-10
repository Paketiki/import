# app/api/movies.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.models.users import User
from app.services.movies import MovieService
from app.schemas.movies import MovieCreate, MovieUpdate, MovieInDB, MovieResponse
from app.database.database import get_db

router = APIRouter()



router = APIRouter(tags=["movies"])

class Movie(BaseModel):
    id: int
    title: str
    year: int
    rating: float
    genre: str
    poster_url: Optional[str] = None
    overview: Optional[str] = None
    picks: List[str] = []

# Демо-фильмы
DEMO_MOVIES = [
    {
        "id": 1,
        "title": "Интерстеллар",
        "year": 2014,
        "rating": 8.6,
        "genre": "Фантастика, Драма",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg",
        "overview": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планету с подходящими для человечества условиями.",
        "picks": ["hits", "classic"]
    },
    {
        "id": 2,
        "title": "Начало",
        "year": 2010,
        "rating": 8.8,
        "genre": "Фантастика, Боевик",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg",
        "overview": "Кобб — талантливый вор, лучший из лучших в опасном искусстве извлечения: он крадет ценные секреты из глубин подсознания во время сна, когда человеческий разум наиболее уязвим.",
        "picks": ["hits"]
    }
]



# 1. Сначала конкретные пути
@router.get("/test", include_in_schema=False)  # include_in_schema=False чтобы не показывать в docs
async def test_movies():
    return {"message": "Movies endpoint works"}

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
    
    # Пробуем загрузить из БД
    try:
        movies = await movie_service.get_movies(
            skip=skip,
            limit=limit,
            genre=genre,
            year=year,
            search=search,
            rating_min=rating_min,
            rating_max=rating_max,
            pick=pick
        )
        
        if movies:
            # Преобразуем в нужный формат
            response_movies = []
            for movie in movies:
                # Получаем подборки для фильма
                picks = [pick.slug for pick in movie.picks] if hasattr(movie, 'picks') else []
                
                response_movies.append({
                    "id": movie.id,
                    "title": movie.title,
                    "year": movie.year,
                    "rating": movie.rating,
                    "genre": movie.genre,
                    "poster_url": movie.poster_url,
                    "overview": movie.overview,
                    "picks": picks
                })
            
            return response_movies
    
    except Exception as e:
        print(f"Ошибка загрузки из БД: {e}")
    
    # Если БД не работает, возвращаем демо-данные
    return DEMO_MOVIES

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