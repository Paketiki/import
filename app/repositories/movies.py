# app/repositories/movies.py
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.models.movies import Movie
from app.models.movie_picks import MoviePick
from app.models.picks import Pick
from app.models.users import User
from app.repositories.base import BaseRepository

class MovieRepository(BaseRepository[Movie]):
    def __init__(self, db: AsyncSession):
        super().__init__(Movie, db)
    
    async def get_by_title(self, title: str) -> List[Movie]:
        result = await self.db.execute(
            select(Movie).filter(Movie.title.ilike(f"%{title}%"))
        )
        return result.scalars().all()
    
    async def get_by_genre(self, genre: str, skip: int = 0, limit: int = 100) -> List[Movie]:
        result = await self.db.execute(
            select(Movie)
            .filter(Movie.genre.ilike(f"%{genre}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_title(self, title: str) -> List[Movie]:
        return await self.get_by_title(title)
    
    async def get_by_year_range(self, start_year: int, end_year: int) -> List[Movie]:
        result = await self.db.execute(
            select(Movie)
            .filter(Movie.year >= start_year)
            .filter(Movie.year <= end_year)
        )
        return result.scalars().all()
    
    async def get_all_with_picks(self, **filters) -> List[Movie]:
        query = select(Movie).options(selectinload(Movie.picks))
        
        # Применяем фильтры
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query = query.where(
                or_(
                    Movie.title.ilike(search_term),
                    Movie.description.ilike(search_term),
                    Movie.director.ilike(search_term)
                )
            )
        
        if filters.get('year'):
            query = query.where(Movie.year == filters['year'])
        
        # Добавляем пагинацию
        skip = filters.get('skip', 0)
        limit = filters.get('limit', 100)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().unique().all()
    
    async def add_pick_to_movie(self, movie_id: int, pick_id: int) -> bool:
        # Проверяем, существует ли уже связь
        query = select(MoviePick).where(
            and_(MoviePick.movie_id == movie_id, MoviePick.pick_id == pick_id)
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return False  # Связь уже существует
        
        # Проверяем существование фильма и подборки
        movie_stmt = select(Movie).where(Movie.id == movie_id)
        movie_result = await self.db.execute(movie_stmt)
        movie = movie_result.scalar_one_or_none()
        
        pick_stmt = select(Pick).where(Pick.id == pick_id)
        pick_result = await self.db.execute(pick_stmt)
        pick = pick_result.scalar_one_or_none()
        
        if not movie or not pick:
            return False
        
        # Создаем новую связь
        movie_pick = MoviePick(movie_id=movie_id, pick_id=pick_id)
        self.db.add(movie_pick)
        await self.db.commit()
        return True