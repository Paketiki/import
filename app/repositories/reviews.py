from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, and_, or_
from typing import List, Optional
from app.models.reviews import Review
from app.models.movies import Movie
from .base import BaseRepository

class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: AsyncSession):
        super().__init__(Review, db)
    
    async def get_reviews_by_movie(
        self,
        movie_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"movie_id": movie_id},
            order_by="-created_at"
        )
    
    async def get_reviews_by_user(
        self,
        username: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"username": username},
            order_by="-created_at"
        )
    
    async def get_review_with_movie(self, review_id: int) -> Optional[Review]:
        result = await self.db.execute(
            select(Review)
            .join(Movie)
            .where(Review.id == review_id)
        )
        return result.scalar_one_or_none()