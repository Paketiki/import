# app/api/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.reviews import Review, ReviewCreate, ReviewUpdate, ReviewResponse
from app.services.reviews import ReviewService
from app.database.database import get_db
from app.api.dependencies import get_current_user, get_current_active_user
from app.models.users import User

router = APIRouter()

@router.get("/", response_model=List[ReviewResponse])
async def get_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    movie_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список рецензий с фильтрацией
    """
    reviews = await ReviewService(db).get_reviews(
        skip=skip,
        limit=limit,
        movie_id=movie_id,
        user_id=user_id
    )
    return reviews

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить рецензию по ID
    """
    review = await ReviewService(db).get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецензия не найдена"
        )
    return review

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить рецензию (только автор или администратор/модератор)
    """
    review = await ReviewService(db).get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецензия не найдена"
        )
    
    # Проверка прав доступа
    is_admin_or_moderator = any(role.name in ["Администратор", "Модератор"] for role in current_user.roles)
    is_author = review.user_id == current_user.id
    
    if not (is_author or is_admin_or_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления рецензии"
        )
    
    updated_review = await ReviewService(db).update_review(review_id, review_update)
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецензия не найдена"
        )
    
    # Обновляем средний рейтинг фильма
    await ReviewService(db).update_movie_rating(review.movie_id)
    
    return updated_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удалить рецензию (только автор или администратор/модератор)
    """
    review = await ReviewService(db).get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецензия не найдена"
        )
    
    # Проверка прав доступа
    is_admin_or_moderator = any(role.name in ["Администратор", "Модератор"] for role in current_user.roles)
    is_author = review.user_id == current_user.id
    
    if not (is_author or is_admin_or_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления рецензии"
        )
    
    movie_id = review.movie_id
    
    deleted = await ReviewService(db).delete_review(review_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецензия не найдена"
        )
    
    # Обновляем средний рейтинг фильма
    await ReviewService(db).update_movie_rating(movie_id)
    
    return None

# Добавим отдельный endpoint для удаления рецензий в контексте фильма
@router.delete("/movies/{movie_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie_review(
    movie_id: int,
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удалить рецензию для конкретного фильма
    """
    # Проверяем, существует ли фильм
    from app.services.movies import MovieService
    movie = await MovieService(db).get_movie(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )
    
    # Проверяем, существует ли рецензия и принадлежит ли фильму
    review = await ReviewService(db).get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецензия не найдена"
        )
    
    if review.movie_id != movie_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Рецензия не принадлежит указанному фильму"
        )
    
    # Проверка прав доступа
    is_admin_or_moderator = any(role.name in ["Администратор", "Модератор"] for role in current_user.roles)
    is_author = review.user_id == current_user.id
    
    if not (is_author or is_admin_or_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления рецензии"
        )
    
    deleted = await ReviewService(db).delete_review(review_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецензия не найдена"
        )
    
    # Обновляем средний рейтинг фильма
    await ReviewService(db).update_movie_rating(movie_id)
    
    return None