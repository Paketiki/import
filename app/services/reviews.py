# app/services/reviews.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, func, desc

from app.models.reviews import Review
from app.models.movies import Movie
from app.models.users import User
from app.schemas.reviews import ReviewCreate, ReviewUpdate

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_reviews(self, skip: int = 0, limit: int = 100, 
                         movie_id: Optional[int] = None,
                         user_id: Optional[int] = None) -> List[Review]:
        stmt = select(Review).options(
            select(Review.movie),
            select(Review.user)
        )
        
        if movie_id:
            stmt = stmt.where(Review.movie_id == movie_id)
        
        if user_id:
            stmt = stmt.where(Review.user_id == user_id)
        
        stmt = stmt.offset(skip).limit(limit).order_by(desc(Review.created_at))
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_reviews_by_movie(self, movie_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return await self.get_reviews(skip=skip, limit=limit, movie_id=movie_id)
    
    async def get_review(self, review_id: int) -> Optional[Review]:
        stmt = select(Review).where(Review.id == review_id).options(
            select(Review.movie),
            select(Review.user)
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_review(self, movie_id: int, user_id: int, review_data: ReviewCreate) -> Review:
        # Проверяем, существует ли фильм
        movie_stmt = select(Movie).where(Movie.id == movie_id)
        movie_result = await self.db.execute(movie_stmt)
        movie = movie_result.scalar_one_or_none()
        
        if not movie:
            raise ValueError("Фильм не найден")
        
        # Проверяем, существует ли пользователь
        user_stmt = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Создаем рецензию
        review = Review(
            movie_id=movie_id,
            user_id=user_id,
            author=review_data.author if review_data.author else user.username,
            role=review_data.role if review_data.role else "Зритель",
            rating=review_data.rating,
            text=review_data.text
        )
        
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        
        # Обновляем средний рейтинг фильма
        from .movies import MovieService
        movie_service = MovieService(self.db)
        await movie_service.update_movie_rating(movie_id)
        
        return review
    
    async def update_review(self, review_id: int, review_update: ReviewUpdate) -> Optional[Review]:
        stmt = select(Review).where(Review.id == review_id)
        result = await self.db.execute(stmt)
        review = result.scalar_one_or_none()
        
        if not review:
            return None
        
        update_data = review_update.dict(exclude_unset=True)
        
        # Обновляем поля
        for key, value in update_data.items():
            if hasattr(review, key):
                setattr(review, key, value)
        
        await self.db.commit()
        await self.db.refresh(review)
        
        # Обновляем средний рейтинг фильма
        from .movies import MovieService
        movie_service = MovieService(self.db)
        await movie_service.update_movie_rating(review.movie_id)
        
        return review
    
    async def delete_review(self, review_id: int) -> bool:
        stmt = select(Review).where(Review.id == review_id)
        result = await self.db.execute(stmt)
        review = result.scalar_one_or_none()
        
        if not review:
            return False
        
        movie_id = review.movie_id
        
        await self.db.delete(review)
        await self.db.commit()
        
        # Обновляем средний рейтинг фильма
        from .movies import MovieService
        movie_service = MovieService(self.db)
        await movie_service.update_movie_rating(movie_id)
        
        return True