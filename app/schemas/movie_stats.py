# app/schemas/movie_stats.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MovieStatBase(BaseModel):
    movie_id: int
    views_count: int = 0
    average_rating: float = 0.0
    reviews_count: int = 0
    picks_count: int = 0

class MovieStatCreate(MovieStatBase):
    pass

class MovieStatUpdate(MovieStatBase):
    pass

class MovieStat(MovieStatBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MovieStatWithMovie(MovieStat):
    movie_title: Optional[str] = None
    movie_release_year: Optional[int] = None
    
    class Config:
        from_attributes = True