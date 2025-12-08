from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from .picks import PickInDB
from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    title: str = Field(..., max_length=255)
    release_year: int = Field(..., ge=1890, le=2030)
    genre: str = Field(..., max_length=100)
    rating: float = Field(..., ge=0, le=10)
    poster: Optional[str] = Field(None, max_length=500)
    overview: Optional[str] = None
    review: Optional[str] = None

class MovieCreate(BaseModel):
    title: str
    release_year: Optional[int] = None
    genre: Optional[str] = None
    duration: Optional[int] = None
    rating: Optional[float] = None
    poster: Optional[str] = Field(None, max_length=500)
    overview: Optional[str] = None
    review: Optional[str] = None 

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    release_year: Optional[int] = Field(None, ge=1890, le=2030)
    genre: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=0, le=10)
    poster: Optional[str] = Field(None, max_length=500)
    overview: Optional[str] = None
    review: Optional[str] = None

class MovieInDB(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MovieWithPicks(MovieInDB):
    picks: List[PickInDB] = []