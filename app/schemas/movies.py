# app/schemas/movies.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MovieBase(BaseModel):
    title: str
    overview: Optional[str] = None
    year: int
    genre: str
    rating: float = Field(ge=0.0, le=10.0)
    poster_url: Optional[str] = None

class MovieCreate(MovieBase):
    picks: List[str] = []
    created_by: Optional[int] = None

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    overview: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    rating: Optional[float] = None
    poster_url: Optional[str] = None

class MovieResponse(MovieBase):
    id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MovieDetailResponse(MovieResponse):
    picks: List[str] = []
    reviews_count: int = 0
    
    class Config:
        from_attributes = True