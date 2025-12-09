# app/repositories/movie_stats.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.movie_stats import MovieStat
from app.models.movies import Movie
from app.schemas.movie_stats import MovieStatCreate, MovieStatUpdate

class MovieStatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, stat_id: int) -> Optional[MovieStat]:
        stmt = select(MovieStat).where(MovieStat.id == stat_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_movie_id(self, movie_id: int) -> Optional[MovieStat]:
        stmt = select(MovieStat).where(MovieStat.movie_id == movie_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MovieStat]:
        stmt = select(MovieStat).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_with_movies(self, skip: int = 0, limit: int = 100) -> List[MovieStat]:
        stmt = (select(MovieStat)
                .join(Movie, MovieStat.movie_id == Movie.id)
                .options(selectinload(MovieStat.movie))
                .offset(skip).limit(limit))
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, stat: MovieStatCreate) -> Optional[MovieStat]:
        # Проверяем существование фильма
        movie_stmt = select(Movie).where(Movie.id == stat.movie_id)
        movie_result = await self.db.execute(movie_stmt)
        movie = movie_result.scalar_one_or_none()
        
        if not movie:
            return None
        
        db_stat = MovieStat(**stat.dict())
        self.db.add(db_stat)
        await self.db.commit()
        await self.db.refresh(db_stat)
        
        return db_stat
    
    async def update(self, stat_id: int, stat: MovieStatUpdate) -> Optional[MovieStat]:
        db_stat = await self.get_by_id(stat_id)
        if db_stat:
            update_data = stat.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_stat, key, value)
            
            await self.db.commit()
            await self.db.refresh(db_stat)
        
        return db_stat
    
    async def delete(self, stat_id: int) -> bool:
        db_stat = await self.get_by_id(stat_id)
        if db_stat:
            await self.db.delete(db_stat)
            await self.db.commit()
            return True
        return False
    
    async def increment_views(self, movie_id: int) -> Optional[MovieStat]:
        stat = await self.get_by_movie_id(movie_id)
        if stat:
            stat.views_count += 1
            await self.db.commit()
            await self.db.refresh(stat)
        
        return stat
    
    async def update_average_rating(self, movie_id: int, average_rating: float) -> Optional[MovieStat]:
        stat = await self.get_by_movie_id(movie_id)
        if stat:
            stat.average_rating = average_rating
            await self.db.commit()
            await self.db.refresh(stat)
        
        return stat