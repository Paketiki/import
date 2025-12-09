# app/services/movie_picks.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.movie_picks import MoviePick
from app.models.movies import Movie
from app.models.picks import Pick
from app.models.users import User
from app.schemas.movie_picks import MoviePickCreate, MoviePickUpdate

class MoviePickService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_movie_pick(self, pick_id: int) -> Optional[MoviePick]:
        stmt = select(MoviePick).where(MoviePick.id == pick_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_movie_picks_by_movie(self, movie_id: int) -> List[MoviePick]:
        stmt = select(MoviePick).where(MoviePick.movie_id == movie_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_movie_picks_by_pick(self, pick_id: int) -> List[MoviePick]:
        stmt = select(MoviePick).where(MoviePick.pick_id == pick_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_all_movie_picks(self, skip: int = 0, limit: int = 100) -> List[MoviePick]:
        stmt = select(MoviePick).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create_movie_pick(self, movie_pick: MoviePickCreate) -> MoviePick:
        # Проверяем существование фильма
        movie_stmt = select(Movie).where(Movie.id == movie_pick.movie_id)
        movie_result = await self.db.execute(movie_stmt)
        movie = movie_result.scalar_one_or_none()
        
        if not movie:
            raise ValueError(f"Фильм с ID {movie_pick.movie_id} не найден")
        
        # Проверяем существование подборки
        pick_stmt = select(Pick).where(Pick.id == movie_pick.pick_id)
        pick_result = await self.db.execute(pick_stmt)
        pick = pick_result.scalar_one_or_none()
        
        if not pick:
            raise ValueError(f"Подборка с ID {movie_pick.pick_id} не найден")
        
        # Проверяем существование пользователя
        user_stmt = select(User).where(User.id == movie_pick.added_by)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"Пользователь с ID {movie_pick.added_by} не найден")
        
        # Проверяем, существует ли уже такая связь
        existing_stmt = select(MoviePick).where(
            MoviePick.movie_id == movie_pick.movie_id,
            MoviePick.pick_id == movie_pick.pick_id
        )
        existing_result = await self.db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise ValueError("Этот фильм уже добавлен в эту подборку")
        
        # Создаем связь
        new_pick = MoviePick(
            movie_id=movie_pick.movie_id,
            pick_id=movie_pick.pick_id,
            added_by=movie_pick.added_by
        )
        
        self.db.add(new_pick)
        await self.db.commit()
        await self.db.refresh(new_pick)
        
        return new_pick
    
    async def update_movie_pick(self, pick_id: int, movie_pick: MoviePickUpdate) -> Optional[MoviePick]:
        stmt = select(MoviePick).where(MoviePick.id == pick_id)
        result = await self.db.execute(stmt)
        db_pick = result.scalar_one_or_none()
        
        if not db_pick:
            return None
        
        # Проверяем уникальность если изменены movie_id или pick_id
        if movie_pick.movie_id != db_pick.movie_id or movie_pick.pick_id != db_pick.pick_id:
            existing_stmt = select(MoviePick).where(
                MoviePick.movie_id == movie_pick.movie_id,
                MoviePick.pick_id == movie_pick.pick_id
            )
            existing_result = await self.db.execute(existing_stmt)
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                raise ValueError("Этот фильм уже добавлен в эту подборку")
        
        db_pick.movie_id = movie_pick.movie_id
        db_pick.pick_id = movie_pick.pick_id
        db_pick.added_by = movie_pick.added_by
        
        await self.db.commit()
        await self.db.refresh(db_pick)
        
        return db_pick
    
    async def delete_movie_pick(self, pick_id: int) -> bool:
        stmt = select(MoviePick).where(MoviePick.id == pick_id)
        result = await self.db.execute(stmt)
        db_pick = result.scalar_one_or_none()
        
        if not db_pick:
            return False
        
        await self.db.delete(db_pick)
        await self.db.commit()
        
        return True