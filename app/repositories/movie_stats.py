# app/repositories/movie_stats.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.movie_stats import MovieStat 
from app.models.movies import Movie
from app.schemas.movie_stats import MovieStatCreate, MovieStatUpdate

class MovieStatRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, stat_id: int) -> Optional[MovieStat]:
        return self.db.query(MovieStat).filter(MovieStat.id == stat_id).first()
    
    def get_by_movie_id(self, movie_id: int) -> Optional[MovieStat]:
        return self.db.query(MovieStat).filter(MovieStat.movie_id == movie_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[MovieStat]:
        return self.db.query(MovieStat).offset(skip).limit(limit).all()
    
    def get_with_movies(self, skip: int = 0, limit: int = 100) -> List[MovieStat]:
        return self.db.query(MovieStat).join(Movie).offset(skip).limit(limit).all()
    
    def create(self, stat: MovieStatCreate) -> Optional[MovieStat]:
        # Проверяем существование фильма
        movie = self.db.query(Movie).filter(Movie.id == stat.movie_id).first()
        if not movie:
            return None
        
        db_stat = MovieStat(**stat.dict())
        self.db.add(db_stat)
        self.db.commit()
        self.db.refresh(db_stat)
        return db_stat
    
    def update(self, stat_id: int, stat: MovieStatUpdate) -> Optional[MovieStat]:
        db_stat = self.get_by_id(stat_id)
        if db_stat:
            for key, value in stat.dict(exclude_unset=True).items():
                setattr(db_stat, key, value)
            self.db.commit()
            self.db.refresh(db_stat)
        return db_stat
    
    def delete(self, stat_id: int) -> bool:
        db_stat = self.get_by_id(stat_id)
        if db_stat:
            self.db.delete(db_stat)
            self.db.commit()
            return True
        return False
    
    def increment_views(self, movie_id: int) -> Optional[MovieStat]:
        stat = self.get_by_movie_id(movie_id)
        if stat:
            stat.views_count += 1
            self.db.commit()
            self.db.refresh(stat)
        return stat
    
    def update_average_rating(self, movie_id: int, average_rating: float) -> Optional[MovieStat]:
        stat = self.get_by_movie_id(movie_id)
        if stat:
            stat.average_rating = average_rating
            self.db.commit()
            self.db.refresh(stat)
        return stat