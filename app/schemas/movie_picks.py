# app/schemas/movie_picks.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MoviePickBase(BaseModel):
    movie_id: int
    pick_id: int
    added_by: int

class MoviePickCreate(MoviePickBase):
    pass

class MoviePickUpdate(MoviePickBase):
    pass

class MoviePick(MoviePickBase):
    id: int
    added_at: datetime
    
    class Config:
        from_attributes = True

class MoviePickWithDetails(MoviePick):
    movie_title: Optional[str] = None
    pick_name: Optional[str] = None
    added_by_username: Optional[str] = None
    
    class Config:
        from_attributes = True