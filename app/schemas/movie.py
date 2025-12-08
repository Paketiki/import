from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field, validator


class MovieCreate(BaseModel):
    title: str
    release_year: Optional[int] = None
    genre: Optional[str] = None
    duration: Optional[int] = None
    rating: Optional[float] = None
    poster: Optional[str] = Field(None, max_length=500)
    overview: Optional[str] = None
    review: Optional[str] = None 
