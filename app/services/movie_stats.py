# app/services/movie_stats.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.movie_stats import MovieStatRepository
from app.schemas.movie_stats import MovieStatCreate, MovieStatUpdate, MovieStat, MovieStatWithMovie
from app.exceptions.base import NotFoundException, ConflictException

class MovieStatService:
    def __init__(self, db: Session):
        self.repository = MovieStatRepository(db)
    
    def get_movie_stat(self, stat_id: int) -> Optional[MovieStat]:
        stat = self.repository.get_by_id(stat_id)
        if not stat:
            raise NotFoundException("Статистика не найдена")
        return stat
    
    def get_movie_stat_by_movie(self, movie_id: int) -> Optional[MovieStat]:
        stat = self.repository.get_by_movie_id(movie_id)
        if not stat:
            raise NotFoundException("Статистика для этого фильма не найдена")
        return stat
    
    def get_all_movie_stats(self, skip: int = 0, limit: int = 100) -> List[MovieStat]:
        return self.repository.get_all(skip, limit)
    
    def get_all_movie_stats_with_movies(self, skip: int = 0, limit: int = 100) -> List[MovieStatWithMovie]:
        stats = self.repository.get_with_movies(skip, limit)
        result = []
        for stat in stats:
            stat_dict = {**stat.__dict__}
            if hasattr(stat, 'movie'):
                stat_dict['movie_title'] = stat.movie.title
                stat_dict['movie_release_year'] = stat.movie.release_year
            result.append(MovieStatWithMovie(**stat_dict))
        return result
    
    def create_movie_stat(self, stat: MovieStatCreate) -> MovieStat:
        # Проверяем существование статистики для этого фильма
        existing_stat = self.repository.get_by_movie_id(stat.movie_id)
        if existing_stat:
            raise ConflictException("Статистика для этого фильма уже существует")
        
        new_stat = self.repository.create(stat)
        if not new_stat:
            raise NotFoundException("Фильм не найден")
        
        return new_stat
    
    def update_movie_stat(self, stat_id: int, stat: MovieStatUpdate) -> MovieStat:
        db_stat = self.repository.get_by_id(stat_id)
        if not db_stat:
            raise NotFoundException("Статистика не найдена")
        
        updated_stat = self.repository.update(stat_id, stat)
        if not updated_stat:
            raise NotFoundException("Статистика не найдена")
        
        return updated_stat
    
    def delete_movie_stat(self, stat_id: int) -> bool:
        db_stat = self.repository.get_by_id(stat_id)
        if not db_stat:
            raise NotFoundException("Статистика не найдена")
        
        return self.repository.delete(stat_id)
    
    def increment_views(self, movie_id: int) -> MovieStat:
        stat = self.repository.increment_views(movie_id)
        if not stat:
            raise NotFoundException("Статистика для этого фильма не найдена")
        return stat
    
    def update_average_rating(self, movie_id: int, average_rating: float) -> MovieStat:
        stat = self.repository.update_average_rating(movie_id, average_rating)
        if not stat:
            raise NotFoundException("Статистика для этого фильма не найдена")
        return stat