# Создайте файл favorites.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .movies import MovieInDB

class FavoriteBase(BaseModel):
    movie_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteInDB(FavoriteBase):
    id: int
    user_id: int
    movie: Optional[MovieInDB] = None
    created_at: datetime
    
    class Config:
        from_attributes = True