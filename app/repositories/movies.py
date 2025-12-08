from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import Dict, List, Optional, Tuple
from app.models.movies import Movie, MoviePick
from app.models.picks import Pick
from app.models.reviews import Review
from .base import BaseRepository

class MovieRepository(BaseRepository[Movie]):
    def __init__(self, db: AsyncSession):
        super().__init__(Movie, db)
    
    async def get_with_picks(self, movie_id: int) -> Optional[Movie]:
        result = await self.db.execute(
            select(Movie)
            .options(selectinload(Movie.picks))
            .where(Movie.id == movie_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_picks(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        year: Optional[int] = None,
        genre: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        pick_name: Optional[str] = None
    ) -> List[Movie]:
        query = select(Movie).options(selectinload(Movie.picks))
        
        if search:
            query = query.where(
                or_(
                    Movie.title.ilike(f"%{search}%"),
                    Movie.overview.ilike(f"%{search}%")
                )
            )
        
        if year:
            query = query.where(Movie.release_year == year)
        
        if genre:
            query = query.where(Movie.genre.ilike(f"%{genre}%"))
        
        if min_rating:
            query = query.where(Movie.rating >= min_rating)
        
        if max_rating:
            query = query.where(Movie.rating <= max_rating)
        
        if pick_name:
            query = query.join(Movie.picks).where(Pick.name == pick_name)
        
        query = query.order_by(desc(Movie.rating)).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        movies = result.scalars().all()
        return movies
    
    async def get_top_movies(self, limit: int = 10) -> List[Movie]:
        result = await self.db.execute(
            select(Movie)
            .options(selectinload(Movie.picks))
            .order_by(desc(Movie.rating))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def add_pick_to_movie(self, movie_id: int, pick_id: int) -> bool:
        # Check if relationship already exists
        result = await self.db.execute(
            select(MoviePick).where(
                and_(
                    MoviePick.movie_id == movie_id,
                    MoviePick.pick_id == pick_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            db_movie_pick = MoviePick(movie_id=movie_id, pick_id=pick_id)
            self.db.add(db_movie_pick)
            await self.db.commit()
        
        return True
    
    async def remove_pick_from_movie(self, movie_id: int, pick_id: int) -> bool:
        result = await self.db.execute(
            delete(MoviePick).where(
                and_(
                    MoviePick.movie_id == movie_id,
                    MoviePick.pick_id == pick_id
                )
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_movie_stats(self, movie_id: int) -> Dict:
        # Get average user rating and review count
        result = await self.db.execute(
            select(
                func.count(Review.id).label("review_count"),
                func.avg(Review.rating).label("avg_rating")
            ).where(Review.movie_id == movie_id)
        )
        stats = result.first()
        
        return {
            "review_count": stats.review_count or 0,
            "avg_user_rating": float(stats.avg_rating) if stats.avg_rating else 0.0
        }