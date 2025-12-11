"""Единый API для КиноВзора с поддержкой:
- Фильмов (сохранение в БД)
- Отзывов (сохранение и удаление)
- Избранного (сохранение по пользователям)
- Аутентификации
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.database.database import get_db
from app.models.movies import Movie
from app.models.reviews import Review
from app.models.favorites import Favorite
from app.models.users import User
from app.models.picks import Pick
from app.models.movie_picks import MoviePick
from app.api.dependencies import get_current_user

# Роутер
router = APIRouter()

# ============================================================================
# ФИЛЬМЫ
# ============================================================================

@router.get("/movies", tags=["Movies"])
async def get_movies(db: Session = Depends(get_db)):
    """
    Получить список всех фильмов с подборками
    """
    movies = db.query(Movie).all()
    result = []
    
    for movie in movies:
        picks = db.query(Pick.name).join(
            MoviePick, MoviePick.pick_id == Pick.id
        ).filter(
            MoviePick.movie_id == movie.id
        ).all()
        
        result.append({
            "id": movie.id,
            "title": movie.title,
            "overview": movie.overview,
            "year": movie.year,
            "genre": movie.genre,
            "rating": movie.rating,
            "poster_url": movie.poster_url,
            "picks": [p[0] for p in picks],
            "created_by": movie.created_by
        })
    
    return result


@router.get("/movies/{movie_id}", tags=["Movies"])
async def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о конкретном фильме
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    picks = db.query(Pick.name).join(
        MoviePick, MoviePick.pick_id == Pick.id
    ).filter(
        MoviePick.movie_id == movie_id
    ).all()
    
    return {
        "id": movie.id,
        "title": movie.title,
        "overview": movie.overview,
        "year": movie.year,
        "genre": movie.genre,
        "rating": movie.rating,
        "poster_url": movie.poster_url,
        "picks": [p[0] for p in picks],
        "created_by": movie.created_by
    }


@router.post("/movies", tags=["Movies"])
async def create_movie(
    title: str,
    year: int,
    genre: str,
    rating: float,
    overview: Optional[str] = None,
    poster_url: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый фильм (только админ)
    """
    # Проверяем, что это админ
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="u0422олько администратор может добавлять фильмы"
        )
    
    movie = Movie(
        title=title,
        year=year,
        genre=genre,
        rating=rating,
        overview=overview,
        poster_url=poster_url,
        created_by=current_user.id
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    return {
        "id": movie.id,
        "title": movie.title,
        "year": movie.year,
        "genre": movie.genre,
        "rating": movie.rating,
        "created_by": movie.created_by
    }


# ============================================================================
# ОТЗЫВЫ
# ============================================================================

@router.get("/reviews", tags=["Reviews"])
async def get_reviews(movie_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Получить все отзывы (опционально фильтровать по фильму)
    """
    query = db.query(Review)
    
    if movie_id:
        query = query.filter(Review.movie_id == movie_id)
    
    reviews = query.all()
    result = []
    
    for review in reviews:
        result.append({
            "id": review.id,
            "movie_id": review.movie_id,
            "user_id": review.user_id,
            "author_name": review.author_name or (review.user.username if review.user else "Аноним"),
            "text": review.text,
            "rating": review.rating,
            "created_at": review.created_at.isoformat() if review.created_at else None
        })
    
    return result


@router.post("/reviews", tags=["Reviews"])
async def create_review(
    movie_id: int,
    text: str,
    rating: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый отзыв на фильм
    """
    # Проверяем, что фильм существует
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    review = Review(
        movie_id=movie_id,
        user_id=current_user.id,
        text=text,
        rating=rating,
        author_name=current_user.username
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return {
        "id": review.id,
        "movie_id": review.movie_id,
        "user_id": review.user_id,
        "author_name": review.author_name,
        "text": review.text,
        "rating": review.rating,
        "created_at": review.created_at.isoformat() if review.created_at else None
    }


@router.delete("/reviews/{review_id}", tags=["Reviews"])
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить отзыв (только админ или автор отзыва)
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="u041eтзыв не найден")
    
    # Проверяем, что ето админ или автор отзыва
    if not current_user.is_superuser and review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="u0412ы не можете удалить этот отзыв"
        )
    
    db.delete(review)
    db.commit()
    
    return {"status": "deleted", "review_id": review_id}


# ============================================================================
# ИЗБРАННОЕ
# ============================================================================

@router.get("/favorites", tags=["Favorites"])
async def get_user_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить избранные фильмы текущего пользователя
    """
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    result = []
    
    for fav in favorites:
        movie = fav.movie
        picks = db.query(Pick.name).join(
            MoviePick, MoviePick.pick_id == Pick.id
        ).filter(
            MoviePick.movie_id == movie.id
        ).all()
        
        result.append({
            "id": movie.id,
            "title": movie.title,
            "overview": movie.overview,
            "year": movie.year,
            "genre": movie.genre,
            "rating": movie.rating,
            "poster_url": movie.poster_url,
            "picks": [p[0] for p in picks]
        })
    
    return result


@router.post("/favorites/{movie_id}", tags=["Favorites"])
async def add_to_favorites(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Добавить фильм в избранное
    """
    # Проверяем фильм
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    # Проверяем, что не добавлено уже
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.movie_id == movie_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Фильм уже в избранном")
    
    favorite = Favorite(user_id=current_user.id, movie_id=movie_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return {"status": "added", "movie_id": movie_id}


@router.delete("/favorites/{movie_id}", tags=["Favorites"])
async def remove_from_favorites(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить фильм из избранного
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.movie_id == movie_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Фильм не в избранном")
    
    db.delete(favorite)
    db.commit()
    
    return {"status": "removed", "movie_id": movie_id}


@router.get("/favorites/check/{movie_id}", tags=["Favorites"])
async def check_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Проверить, есть ли фильм в избранном
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.movie_id == movie_id
    ).first()
    
    return {"is_favorite": favorite is not None}


# ============================================================================
# НАВИГАЦИОННЫЕ ЭНдПОИНтЫ
# ============================================================================

@router.get("/search", tags=["Search"])
async def search_movies(q: str, db: Session = Depends(get_db)):
    """
    Поиск фильмов по названию
    """
    if not q or len(q) < 2:
        return []
    
    movies = db.query(Movie).filter(
        Movie.title.ilike(f"%{q}%")
    ).limit(20).all()
    
    result = []
    for movie in movies:
        picks = db.query(Pick.name).join(
            MoviePick, MoviePick.pick_id == Pick.id
        ).filter(
            MoviePick.movie_id == movie.id
        ).all()
        
        result.append({
            "id": movie.id,
            "title": movie.title,
            "year": movie.year,
            "genre": movie.genre,
            "rating": movie.rating,
            "poster_url": movie.poster_url,
            "picks": [p[0] for p in picks]
        })
    
    return result


@router.get("/genres", tags=["Metadata"])
async def get_genres(db: Session = Depends(get_db)):
    """
    Получить список всех жанров
    """
    movies = db.query(Movie.genre).distinct().all()
    genres = set()
    
    for (genre_str,) in movies:
        if genre_str:
            if ',' in genre_str:
                genres.update([g.strip() for g in genre_str.split(',')])
            else:
                genres.add(genre_str.strip())
    
    return sorted(list(genres))


@router.get("/stats", tags=["Metadata"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Получить общую статистику
    """
    movies_count = db.query(Movie).count()
    reviews_count = db.query(Review).count()
    users_count = db.query(User).count()
    
    return {
        "total_movies": movies_count,
        "total_reviews": reviews_count,
        "total_users": users_count
    }
