# app/repositories/movie_picks.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.movies import MoviePick
from app.models.movies import Movie
from app.models.picks import Pick
from app.models.users import User
from app.schemas.movie_picks import MoviePickCreate, MoviePickUpdate

class MoviePickRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, pick_id: int) -> Optional[MoviePick]:
        return self.db.query(MoviePick).filter(MoviePick.id == pick_id).first()
    
    def get_by_movie_and_pick(self, movie_id: int, pick_id: int) -> Optional[MoviePick]:
        return self.db.query(MoviePick).filter(
            and_(MoviePick.movie_id == movie_id, MoviePick.pick_id == pick_id)
        ).first()
    
    def get_by_movie_id(self, movie_id: int) -> List[MoviePick]:
        return self.db.query(MoviePick).filter(MoviePick.movie_id == movie_id).all()
    
    def get_by_pick_id(self, pick_id: int) -> List[MoviePick]:
        return self.db.query(MoviePick).filter(MoviePick.pick_id == pick_id).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[MoviePick]:
        return self.db.query(MoviePick).offset(skip).limit(limit).all()
    
    def get_with_details(self, skip: int = 0, limit: int = 100) -> List[MoviePick]:
        return (self.db.query(MoviePick)
                .join(Movie, MoviePick.movie_id == Movie.id)
                .join(Pick, MoviePick.pick_id == Pick.id)
                .join(User, MoviePick.added_by == User.id)
                .offset(skip).limit(limit).all())
    
    def create(self, movie_pick: MoviePickCreate) -> Optional[MoviePick]:
        # Проверяем существование связанных сущностей
        movie = self.db.query(Movie).filter(Movie.id == movie_pick.movie_id).first()
        pick = self.db.query(Pick).filter(Pick.id == movie_pick.pick_id).first()
        user = self.db.query(User).filter(User.id == movie_pick.added_by).first()
        
        if not all([movie, pick, user]):
            return None
        
        # Проверяем дубликат
        existing = self.get_by_movie_and_pick(movie_pick.movie_id, movie_pick.pick_id)
        if existing:
            return None
        
        db_movie_pick = MoviePick(**movie_pick.dict())
        self.db.add(db_movie_pick)
        self.db.commit()
        self.db.refresh(db_movie_pick)
        
        # Обновляем счетчик в movie_stats
        from app.repositories.movie_stats import MovieStatRepository
        stat_repo = MovieStatRepository(self.db)
        stat = stat_repo.get_by_movie_id(movie_pick.movie_id)
        if stat:
            stat.picks_count += 1
            self.db.commit()
        
        return db_movie_pick
    
    def update(self, pick_id: int, movie_pick: MoviePickUpdate) -> Optional[MoviePick]:
        db_pick = self.get_by_id(pick_id)
        if db_pick:
            for key, value in movie_pick.dict(exclude_unset=True).items():
                setattr(db_pick, key, value)
            self.db.commit()
            self.db.refresh(db_pick)
        return db_pick
    
    def delete(self, pick_id: int) -> bool:
        db_pick = self.get_by_id(pick_id)
        if db_pick:
            movie_id = db_pick.movie_id
            self.db.delete(db_pick)
            self.db.commit()
            
            # Обновляем счетчик в movie_stats
            from app.repositories.movie_stats import MovieStatRepository
            stat_repo = MovieStatRepository(self.db)
            stat = stat_repo.get_by_movie_id(movie_id)
            if stat and stat.picks_count > 0:
                stat.picks_count -= 1
                self.db.commit()
            
            return True
        return False