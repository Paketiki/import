# app/services/movie_picks.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.movie_picks import MoviePickRepository
from app.schemas.movie_picks import MoviePickCreate, MoviePickUpdate, MoviePick, MoviePickWithDetails
from app.exceptions.base import NotFoundException, ConflictException, BadRequestException

class MoviePickService:
    def __init__(self, db: Session):
        self.repository = MoviePickRepository(db)
    
    def get_movie_pick(self, pick_id: int) -> Optional[MoviePick]:
        pick = self.repository.get_by_id(pick_id)
        if not pick:
            raise NotFoundException("Связь фильма с подборкой не найдена")
        return pick
    
    def get_movie_pick_with_details(self, pick_id: int) -> Optional[MoviePickWithDetails]:
        pick = self.repository.get_by_id(pick_id)
        if not pick:
            raise NotFoundException("Связь фильма с подборкой не найдена")
        
        pick_dict = {**pick.__dict__}
        if hasattr(pick, 'movie'):
            pick_dict['movie_title'] = pick.movie.title
        if hasattr(pick, 'pick'):
            pick_dict['pick_name'] = pick.pick.name
        if hasattr(pick, 'user'):
            pick_dict['added_by_username'] = pick.user.username
        
        return MoviePickWithDetails(**pick_dict)
    
    def get_movie_picks_by_movie(self, movie_id: int) -> List[MoviePickWithDetails]:
        picks = self.repository.get_by_movie_id(movie_id)
        result = []
        for pick in picks:
            pick_dict = {**pick.__dict__}
            if hasattr(pick, 'movie'):
                pick_dict['movie_title'] = pick.movie.title
            if hasattr(pick, 'pick'):
                pick_dict['pick_name'] = pick.pick.name
            if hasattr(pick, 'user'):
                pick_dict['added_by_username'] = pick.user.username
            result.append(MoviePickWithDetails(**pick_dict))
        return result
    
    def get_movie_picks_by_pick(self, pick_id: int) -> List[MoviePickWithDetails]:
        picks = self.repository.get_by_pick_id(pick_id)
        result = []
        for pick in picks:
            pick_dict = {**pick.__dict__}
            if hasattr(pick, 'movie'):
                pick_dict['movie_title'] = pick.movie.title
            if hasattr(pick, 'pick'):
                pick_dict['pick_name'] = pick.pick.name
            if hasattr(pick, 'user'):
                pick_dict['added_by_username'] = pick.user.username
            result.append(MoviePickWithDetails(**pick_dict))
        return result
    
    def get_all_movie_picks(self, skip: int = 0, limit: int = 100) -> List[MoviePick]:
        return self.repository.get_all(skip, limit)
    
    def get_all_movie_picks_with_details(self, skip: int = 0, limit: int = 100) -> List[MoviePickWithDetails]:
        picks = self.repository.get_with_details(skip, limit)
        result = []
        for pick in picks:
            pick_dict = {**pick.__dict__}
            if hasattr(pick, 'movie'):
                pick_dict['movie_title'] = pick.movie.title
            if hasattr(pick, 'pick'):
                pick_dict['pick_name'] = pick.pick.name
            if hasattr(pick, 'user'):
                pick_dict['added_by_username'] = pick.user.username
            result.append(MoviePickWithDetails(**pick_dict))
        return result
    
    def create_movie_pick(self, movie_pick: MoviePickCreate) -> MoviePick:
        new_pick = self.repository.create(movie_pick)
        if not new_pick:
            raise BadRequestException(
                "Не удалось добавить фильм в подборку. Проверьте существование фильма, подборки и пользователя, или возможно фильм уже добавлен в эту подборку"
            )
        
        return new_pick
    
    def update_movie_pick(self, pick_id: int, movie_pick: MoviePickUpdate) -> MoviePick:
        db_pick = self.repository.get_by_id(pick_id)
        if not db_pick:
            raise NotFoundException("Связь фильма с подборкой не найдена")
        
        updated_pick = self.repository.update(pick_id, movie_pick)
        if not updated_pick:
            raise NotFoundException("Связь фильма с подборкой не найдена")
        
        return updated_pick
    
    def delete_movie_pick(self, pick_id: int) -> bool:
        db_pick = self.repository.get_by_id(pick_id)
        if not db_pick:
            raise NotFoundException("Связь фильма с подборкой не найдена")
        
        return self.repository.delete(pick_id)