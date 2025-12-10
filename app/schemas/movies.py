from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, List
from datetime import datetime
from .picks import PickInDB

class MovieBase(BaseModel):
    title: str = Field(..., max_length=255)
    release_year: int = Field(..., ge=1890, le=2030)
    genre: str = Field(..., max_length=100)
    rating: float = Field(..., ge=0, le=10)
    poster: Optional[str] = Field(None, max_length=500)
    overview: Optional[str] = None
    review: Optional[str] = None

class MovieCreate(MovieBase):
    duration: Optional[int] = None  # Добавлено из кода main.py

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    release_year: Optional[int] = Field(None, ge=1890, le=2030)
    genre: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=0, le=10)
    poster: Optional[str] = Field(None, max_length=500)
    overview: Optional[str] = None
    review: Optional[str] = None
    duration: Optional[int] = None

class MovieInDB(MovieBase):
    id: int
    duration: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MovieWithPicks(MovieInDB):
    picks: List[PickInDB] = []

class MovieFilters(BaseModel):
    search: Optional[str] = None
    genre: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    pick: Optional[str] = None

# В schemas/movies.py добавьте:
class MovieResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    year: int
    genre: str
    rating: Optional[float] = None
    poster_url: Optional[str] = None
    duration: Optional[int] = None
    director: Optional[str] = None
    country: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
# Для обратной совместимости с существующим кодом
Movie = MovieInDB
MovieResponse = MovieInDB  # Используется в API роутерах