from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.repositories.reviews import ReviewRepository
from app.repositories.movies import MovieRepository
from app.repositories.users import UserRepository
from app.schemas.reviews import ReviewCreate, ReviewUpdate, ReviewInDB
from app.schemas.users import UserRole
from app.exceptions import MovieNotFoundError, ReviewNotFoundError, UserNotFoundError, ValidationError

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.review_repo = ReviewRepository(db)
        self.movie_repo = MovieRepository(db)
        self.user_repo = UserRepository(db)
    
    async def get_review(self, review_id: int) -> ReviewInDB:
        review = await self.review_repo.get(review_id)
        if not review:
            raise ReviewNotFoundError(review_id)
        
        return ReviewInDB.from_orm(review)
    
    async def get_reviews_by_movie(
        self,
        movie_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewInDB]:
        # Check if movie exists
        movie = await self.movie_repo.get(movie_id)
        if not movie:
            raise MovieNotFoundError(movie_id)
        
        reviews = await self.review_repo.get_reviews_by_movie(movie_id, skip, limit)
        return [ReviewInDB.from_orm(review) for review in reviews]
    
    async def get_reviews_by_user(
        self,
        username: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewInDB]:
        # Check if user exists
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise UserNotFoundError(username)
        
        reviews = await self.review_repo.get_reviews_by_user(username, skip, limit)
        return [ReviewInDB.from_orm(review) for review in reviews]
    
    async def create_review(self, review_create: ReviewCreate, username: str) -> ReviewInDB:
        # Check if movie exists
        movie = await self.movie_repo.get(review_create.movie_id)
        if not movie:
            raise MovieNotFoundError(review_create.movie_id)
        
        # Check if user exists and get role
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise UserNotFoundError(username)
        
        # Validate rating
        if review_create.rating < 0 or review_create.rating > 10:
            raise ValidationError("Rating must be between 0 and 10")
        
        # Create review
        review_dict = review_create.dict()
        review_dict["username"] = username
        review_dict["role"] = user.role
        
        review = await self.review_repo.create(review_dict)
        return ReviewInDB.from_orm(review)
    
    async def update_review(self, review_id: int, review_update: ReviewUpdate) -> ReviewInDB:
        review = await self.review_repo.get(review_id)
        if not review:
            raise ReviewNotFoundError(review_id)
        
        update_data = review_update.dict(exclude_unset=True)
        
        # Convert role to string if provided
        if "role" in update_data:
            update_data["role"] = update_data["role"].value
        
        updated_review = await self.review_repo.update(review_id, update_data)
        
        if not updated_review:
            raise ReviewNotFoundError(review_id)
        
        return ReviewInDB.from_orm(updated_review)
    
    async def delete_review(self, review_id: int) -> bool:
        review = await self.review_repo.get(review_id)
        if not review:
            raise ReviewNotFoundError(review_id)
        
        return await self.review_repo.delete(review_id)