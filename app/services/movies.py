from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, desc

from app.models.movies import Movie
from app.models.reviews import Review
from app.models.picks import Pick
from app.models.movie_picks import MoviePick
from app.schemas.movies import MovieCreate, MovieUpdate, MovieFilters


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_movies(self, skip: int = 0, limit: int = 100, 
                        filters: Optional[MovieFilters] = None) -> List[Movie]:
        """Получить список фильмов с фильтрацией"""
        stmt = select(Movie)
        
        # Применяем фильтры
        if filters:
            if filters.search:
                search_term = f"%{filters.search}%"
                stmt = stmt.where(
                    or_(
                        Movie.title.ilike(search_term),
                        Movie.overview.ilike(search_term)
                    )
                )
            
            if filters.genre and filters.genre != 'all':
                stmt = stmt.where(Movie.genre == filters.genre)
            
            if filters.min_rating:
                stmt = stmt.where(Movie.rating >= filters.min_rating)
            
            if filters.max_rating:
                stmt = stmt.where(Movie.rating <= filters.max_rating)
            
            if filters.year_from:
                stmt = stmt.where(Movie.year >= filters.year_from)
            
            if filters.year_to:
                stmt = stmt.where(Movie.year <= filters.year_to)
            
            if filters.pick and filters.pick != 'all':
                # Фильтрация по подборкам через таблицу связей
                subquery = select(MoviePick.movie_id).join(
                    Pick, MoviePick.pick_id == Pick.id
                ).where(Pick.slug == filters.pick).subquery()
                
                stmt = stmt.where(Movie.id.in_(subquery))
        
        stmt = stmt.offset(skip).limit(limit).order_by(desc(Movie.rating), desc(Movie.created_at))
        
        result = await self.db.execute(stmt)
        movies = result.scalars().all()
        
        return movies
    
    async def get_movie(self, movie_id: int) -> Optional[Movie]:
        """Получить один фильм по ID"""
        stmt = select(Movie).where(Movie.id == movie_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_movie(self, movie_data: MovieCreate, created_by: Optional[int] = None) -> Movie:
        """Создать новый фильм"""
        movie_dict = movie_data.dict(exclude={'picks'})
        movie_dict['created_by'] = created_by
        
        # Создаем фильм
        movie = Movie(**movie_dict)
        self.db.add(movie)
        await self.db.flush()
        
        # Добавляем подборки если указаны
        if movie_data.picks:
            for pick_slug in movie_data.picks:
                pick_stmt = select(Pick).where(Pick.slug == pick_slug)
                pick_result = await self.db.execute(pick_stmt)
                pick = pick_result.scalar_one_or_none()
                
                if pick:
                    movie_pick = MoviePick(movie_id=movie.id, pick_id=pick.id)
                    self.db.add(movie_pick)
        
        await self.db.commit()
        await self.db.refresh(movie)
        
        return movie
    
    async def update_movie(self, movie_id: int, movie_update: MovieUpdate) -> Optional[Movie]:
        """Обновить фильм"""
        stmt = select(Movie).where(Movie.id == movie_id)
        result = await self.db.execute(stmt)
        movie = result.scalar_one_or_none()
        
        if not movie:
            return None
        
        update_data = movie_update.dict(exclude_unset=True)
        
        # Обновляем поля
        for key, value in update_data.items():
            if hasattr(movie, key) and value is not None:
                setattr(movie, key, value)
        
        await self.db.commit()
        await self.db.refresh(movie)
        
        return movie
    
    async def delete_movie(self, movie_id: int) -> bool:
        """Удалить фильм"""
        stmt = select(Movie).where(Movie.id == movie_id)
        result = await self.db.execute(stmt)
        movie = result.scalar_one_or_none()
        
        if movie:
            await self.db.delete(movie)
            await self.db.commit()
            return True
        
        return False
    
    async def search_movies(self, title: str, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Поиск фильмов по названию"""
        stmt = select(Movie).where(
            Movie.title.ilike(f"%{title}%")
        ).offset(skip).limit(limit).order_by(desc(Movie.rating))
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def update_movie_rating(self, movie_id: int) -> Optional[float]:
        """Обновить средний рейтинг фильма на основе рецензий"""
        # Получаем средний рейтинг из рецензий
        stmt = select(func.avg(Review.rating)).where(Review.movie_id == movie_id)
        result = await self.db.execute(stmt)
        avg_rating = result.scalar()
        
        # Обновляем рейтинг фильма если есть рецензии
        if avg_rating is not None:
            stmt = select(Movie).where(Movie.id == movie_id)
            result = await self.db.execute(stmt)
            movie = result.scalar_one_or_none()
            
            if movie:
                movie.rating = round(float(avg_rating), 1)
                await self.db.commit()
                await self.db.refresh(movie)
        
        return avg_rating
