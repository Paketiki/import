from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from app.repositories.movies import MovieRepository
from app.repositories.picks import PickRepository
from app.schemas.movies import MovieCreate, MovieUpdate, MovieInDB, MovieWithPicks
from app.schemas.picks import PickInDB
from app.exceptions import MovieNotFoundError, PickNotFoundError, ValidationError

class MovieService:
    def __init__(self, db: AsyncSession):
        self.movie_repo = MovieRepository(db)
        self.pick_repo = PickRepository(db)
    
    async def get_movie(self, movie_id: int) -> MovieWithPicks:
        movie = await self.movie_repo.get_with_picks(movie_id)
        if not movie:
            raise MovieNotFoundError(movie_id)
        
        movie_data = MovieInDB.from_orm(movie).dict()
        picks_data = [PickInDB.from_orm(pick) for pick in movie.picks]
        
        return MovieWithPicks(**movie_data, picks=picks_data)
    
    async def get_movies(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        year: Optional[int] = None,
        genre: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        pick_name: Optional[str] = None
    ) -> List[MovieWithPicks]:
        movies = await self.movie_repo.get_all_with_picks(
            skip=skip,
            limit=limit,
            search=search,
            year=year,
            genre=genre,
            min_rating=min_rating,
            max_rating=max_rating,
            pick_name=pick_name
        )
        
        result = []
        for movie in movies:
            movie_data = MovieInDB.from_orm(movie).dict()
            picks_data = [PickInDB.from_orm(pick) for pick in movie.picks]
            result.append(MovieWithPicks(**movie_data, picks=picks_data))
        
        return result
    
    async def get_top_movies(self, limit: int = 10) -> List[MovieWithPicks]:
        movies = await self.movie_repo.get_top_movies(limit)
        
        result = []
        for movie in movies:
            movie_data = MovieInDB.from_orm(movie).dict()
            picks_data = [PickInDB.from_orm(pick) for pick in movie.picks]
            result.append(MovieWithPicks(**movie_data, picks=picks_data))
        
        return result
    
    async def create_movie(self, movie_create: MovieCreate) -> MovieInDB:
        movie_dict = movie_create.dict()
        movie = await self.movie_repo.create(movie_dict)
        return MovieInDB.from_orm(movie)
    
    async def update_movie(self, movie_id: int, movie_update: MovieUpdate) -> MovieInDB:
        movie = await self.movie_repo.get(movie_id)
        if not movie:
            raise MovieNotFoundError(movie_id)
        
        update_data = movie_update.dict(exclude_unset=True)
        updated_movie = await self.movie_repo.update(movie_id, update_data)
        
        if not updated_movie:
            raise MovieNotFoundError(movie_id)
        
        return MovieInDB.from_orm(updated_movie)
    
    async def delete_movie(self, movie_id: int) -> bool:
        movie = await self.movie_repo.get(movie_id)
        if not movie:
            raise MovieNotFoundError(movie_id)
        
        return await self.movie_repo.delete(movie_id)
    
    async def add_pick_to_movie(self, movie_id: int, pick_id: int) -> bool:
        # Check if movie exists
        movie = await self.movie_repo.get(movie_id)
        if not movie:
            raise MovieNotFoundError(movie_id)
        
        # Check if pick exists
        pick = await self.pick_repo.get(pick_id)
        if not pick:
            raise PickNotFoundError(pick_id)
        
        return await self.movie_repo.add_pick_to_movie(movie_id, pick_id)
    
    async def remove_pick_from_movie(self, movie_id: int, pick_id: int) -> bool:
        return await self.movie_repo.remove_pick_from_movie(movie_id, pick_id)
    
    async def get_movie_stats(self, movie_id: int) -> Dict:
        movie = await self.movie_repo.get(movie_id)
        if not movie:
            raise MovieNotFoundError(movie_id)
        
        stats = await self.movie_repo.get_movie_stats(movie_id)
        return {
            "movie_id": movie_id,
            "title": movie.title,
            "system_rating": float(movie.rating),
            **stats
        }