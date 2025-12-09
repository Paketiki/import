# app/repositories/movie_picks.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.movie_picks import MoviePick
from app.models.movies import Movie
from app.models.picks import Pick
from app.models.users import User
from app.schemas.movie_picks import MoviePickCreate, MoviePickUpdate

class MoviePickRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, pick_id: int) -> Optional[MoviePick]:
        stmt = select(MoviePick).where(MoviePick.id == pick_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_movie_and_pick(self, movie_id: int, pick_id: int) -> Optional[MoviePick]:
        stmt = select(MoviePick).where(
            and_(MoviePick.movie_id == movie_id, MoviePick.pick_id == pick_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_movie_id(self, movie_id: int) -> List[MoviePick]:
        stmt = select(MoviePick).where(MoviePick.movie_id == movie_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_by_pick_id(self, pick_id: int) -> List[MoviePick]:
        stmt = select(MoviePick).where(MoviePick.pick_id == pick_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MoviePick]:
        stmt = select(MoviePick).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_with_details(self, skip: int = 0, limit: int = 100) -> List[MoviePick]:
        stmt = (select(MoviePick)
                .join(Movie, MoviePick.movie_id == Movie.id)
                .join(Pick, MoviePick.pick_id == Pick.id)
                .join(User, MoviePick.added_by == User.id)
                .options(
                    selectinload(MoviePick.movie),
                    selectinload(MoviePick.pick),
                    selectinload(MoviePick.user)
                )
                .offset(skip).limit(limit))
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, movie_pick: MoviePickCreate) -> Optional[MoviePick]:
        # Проверяем существование связанных сущностей
        movie_stmt = select(Movie).where(Movie.id == movie_pick.movie_id)
        movie_result = await self.db.execute(movie_stmt)
        movie = movie_result.scalar_one_or_none()
        
        pick_stmt = select(Pick).where(Pick.id == movie_pick.pick_id)
        pick_result = await self.db.execute(pick_stmt)
        pick = pick_result.scalar_one_or_none()
        
        user_stmt = select(User).where(User.id == movie_pick.added_by)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not all([movie, pick, user]):
            return None
        
        # Проверяем дубликат
        existing = await self.get_by_movie_and_pick(movie_pick.movie_id, movie_pick.pick_id)
        if existing:
            return None
        
        db_movie_pick = MoviePick(**movie_pick.dict())
        self.db.add(db_movie_pick)
        await self.db.commit()
        await self.db.refresh(db_movie_pick)
        
        # Обновляем счетчик в movie_stats
        from app.repositories.movie_stats import MovieStatRepository
        stat_repo = MovieStatRepository(self.db)
        stat = await stat_repo.get_by_movie_id(movie_pick.movie_id)
        if stat:
            stat.picks_count += 1
            await self.db.commit()
        
        return db_movie_pick
    
    async def update(self, pick_id: int, movie_pick: MoviePickUpdate) -> Optional[MoviePick]:
        db_pick = await self.get_by_id(pick_id)
        if db_pick:
            update_data = movie_pick.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_pick, key, value)
            
            await self.db.commit()
            await self.db.refresh(db_pick)
        
        return db_pick
    
    async def delete(self, pick_id: int) -> bool:
        db_pick = await self.get_by_id(pick_id)
        if db_pick:
            movie_id = db_pick.movie_id
            await self.db.delete(db_pick)
            await self.db.commit()
            
            # Обновляем счетчик в movie_stats
            from app.repositories.movie_stats import MovieStatRepository
            stat_repo = MovieStatRepository(self.db)
            stat = await stat_repo.get_by_movie_id(movie_id)
            if stat and stat.picks_count > 0:
                stat.picks_count -= 1
                await self.db.commit()
            
            return True
        return False