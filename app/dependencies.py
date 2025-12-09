# app/utils/dependencies.py (если есть такой файл)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.services.movies import MovieService

async def get_movie_service(db: AsyncSession = Depends(get_db)):
    return MovieService(db)