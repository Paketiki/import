from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database.database import get_db
from app.services.users import UserService
from app.services.movies import MovieService
from app.services.reviews import ReviewService
from app.services.picks import PickService
from app.services.auth import AuthService

# Service dependencies
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

async def get_movie_service(db: AsyncSession = Depends(get_db)) -> MovieService:
    return MovieService(db)

async def get_review_service(db: AsyncSession = Depends(get_db)) -> ReviewService:
    return ReviewService(db)

async def get_pick_service(db: AsyncSession = Depends(get_db)) -> PickService:
    return PickService(db)

def get_auth_service() -> AuthService:
    return AuthService()