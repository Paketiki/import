from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import UserRole

class ReviewBase(BaseModel):
    movie_id: int
    rating: int = Field(..., ge=0, le=10)
    text: str = Field(..., min_length=1)
    role: UserRole

class ReviewCreate(ReviewBase):
    author: Optional[str] = None  # Для JS
    role: Optional[str] = None  # Для JS

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=0, le=10)
    text: Optional[str] = Field(None, min_length=1)
    role: Optional[UserRole] = None

class ReviewInDB(ReviewBase):
    id: int
    username: str
    author: Optional[str] = None  # Алиас для JS
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReviewWithDetails(ReviewInDB):
    movie_title: str

# Для обратной совместимости
Review = ReviewInDB
ReviewResponse = ReviewInDB