# app/services/movies.py
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload

from app.models.movies import Movie
from app.models.reviews import Review
from app.models.users import User
from app.models.picks import Pick
from app.schemas.movies import MovieCreate, MovieInDB, MovieUpdate, MovieFilters
from app.schemas.reviews import ReviewCreate

# app/services/movies.py
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload, selectinload
from app.models.movie_picks import MoviePick


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_movies(self, skip: int = 0, limit: int = 100, 
                        filters: Optional[MovieFilters] = None) -> List[Movie]:
        """Получить список фильмов с фильтрацией"""
        stmt = select(Movie).options(
            selectinload(Movie.picks),
            selectinload(Movie.creator).load_only(User.username)
        )
        
        # Применяем фильтры
        if filters:
            if filters.search:
                search_term = f"%{filters.search}%"
                stmt = stmt.where(
                    or_(
                        Movie.title.ilike(search_term),
                        Movie.description.ilike(search_term),
                        Movie.overview.ilike(search_term),
                        Movie.director.ilike(search_term)
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
                # Фильтрация по подборкам
                subquery = select(MoviePick.movie_id).join(
                    Pick, MoviePick.pick_id == Pick.id
                ).where(Pick.name == filters.pick).subquery()
                
                stmt = stmt.where(Movie.id.in_(subquery))
        
        stmt = stmt.offset(skip).limit(limit).order_by(desc(Movie.rating), desc(Movie.created_at))
        
        result = await self.db.execute(stmt)
        movies = result.scalars().unique().all()
        
        return movies
    
    # app/services/movies.py - проверьте этот метод
async def get_movies(
    self,
    skip: int = 0,
    limit: int = 100,
    **filters
):
    """
    Получить список фильмов с фильтрацией
    """
    query = select(Movie)
    
    if filters.get('genre'):
        query = query.where(Movie.genre.contains(filters['genre']))
    
    if filters.get('year'):
        query = query.where(Movie.year == filters['year'])
    
    if filters.get('search'):
        query = query.where(Movie.title.ilike(f"%{filters['search']}%"))
    
    if filters.get('rating_min'):
        query = query.where(Movie.rating >= filters['rating_min'])
    
    if filters.get('rating_max'):
        query = query.where(Movie.rating <= filters['rating_max'])
    
    query = query.offset(skip).limit(limit)
    result = await self.db.execute(query)
    movies = result.scalars().all()
    
    # Преобразуем в Pydantic модели
    return [MovieInDB.model_validate(movie) for movie in movies]
    
    async def create_movie(self, movie_data: MovieCreate, created_by: int) -> Movie:
        """Создать новый фильм"""
        movie_dict = movie_data.dict(exclude={'picks', 'reviews'})
        movie_dict['created_by'] = created_by
        
        # Создаем фильм
        movie = Movie(**movie_dict)
        self.db.add(movie)
        await self.db.flush()
        
        # Добавляем подборки если указаны
        if hasattr(movie_data, 'picks') and movie_data.picks:
            for pick_name in movie_data.picks:
                pick_stmt = select(Pick).where(Pick.name == pick_name)
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
        
        # Исключаем picks из общего обновления
        picks_data = None
        if 'picks' in update_data:
            picks_data = update_data.pop('picks')
        
        # Обновляем поля
        for key, value in update_data.items():
            if hasattr(movie, key):
                setattr(movie, key, value)
        
        # Обновляем подборки если указаны
        if picks_data is not None:
            # Удаляем старые связи
            delete_stmt = select(MoviePick).where(MoviePick.movie_id == movie_id)
            delete_result = await self.db.execute(delete_stmt)
            old_picks = delete_result.scalars().all()
            
            for old_pick in old_picks:
                await self.db.delete(old_pick)
            
            # Добавляем новые связи
            for pick_name in picks_data:
                pick_stmt = select(Pick).where(Pick.name == pick_name)
                pick_result = await self.db.execute(pick_stmt)
                pick = pick_result.scalar_one_or_none()
                
                if pick:
                    movie_pick = MoviePick(movie_id=movie.id, pick_id=pick.id)
                    self.db.add(movie_pick)
        
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
    
    # ... остальные методы остаются без изменений ...
    
    async def get_user_favorites(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Получить избранные фильмы пользователя"""
        stmt = (
            select(Movie)
            .join(user_favorite_movies, user_favorite_movies.c.movie_id == Movie.id)
            .where(user_favorite_movies.c.user_id == user_id)
            .options(
                joinedload(Movie.picks),
                joinedload(Movie.creator).load_only(User.username)
            )
            .offset(skip)
            .limit(limit)
            .order_by(desc(user_favorite_movies.c.created_at))
        )
        
        result = await self.db.execute(stmt)
        movies = result.scalars().unique().all()
        
        return movies
    
    async def get_user_favorite(self, user_id: int, movie_id: int) -> bool:
        """Проверить, добавлен ли фильм в избранное"""
        stmt = select(func.count('*')).select_from(user_favorite_movies).where(
            and_(
                user_favorite_movies.c.user_id == user_id,
                user_favorite_movies.c.movie_id == movie_id
            )
        )
        
        result = await self.db.execute(stmt)
        count = result.scalar()
        
        return count > 0
    
    async def add_to_favorites(self, user_id: int, movie_id: int) -> bool:
        """Добавить фильм в избранное"""
        # Проверяем, не добавлен ли уже
        if await self.get_user_favorite(user_id, movie_id):
            return False
        
        # Проверяем, существует ли фильм
        movie = await self.get_movie(movie_id)
        if not movie:
            return False
        
        # Добавляем в избранное
        insert_stmt = user_favorite_movies.insert().values(
            user_id=user_id,
            movie_id=movie_id
        )
        
        await self.db.execute(insert_stmt)
        await self.db.commit()
        
        return True
    
    async def remove_from_favorites(self, user_id: int, movie_id: int) -> bool:
        """Удалить фильм из избранного"""
        delete_stmt = user_favorite_movies.delete().where(
            and_(
                user_favorite_movies.c.user_id == user_id,
                user_favorite_movies.c.movie_id == movie_id
            )
        )
        
        result = await self.db.execute(delete_stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
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
    
    async def search_movies(self, title: str, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Поиск фильмов по названию"""
        stmt = select(Movie).where(
            Movie.title.ilike(f"%{title}%")
        ).options(
            joinedload(Movie.picks),
            joinedload(Movie.creator).load_only(User.username)
        ).offset(skip).limit(limit).order_by(desc(Movie.rating))
        
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()