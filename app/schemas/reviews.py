from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    movie_id: int
    text: str
    rating: float = Field(ge=1.0, le=10.0)
    author_name: Optional[str] = None

class ReviewCreate(ReviewBase):
    user_id: Optional[int] = None

class ReviewUpdate(BaseModel):
    text: Optional[str] = None
    rating: Optional[float] = None

class ReviewResponse(ReviewBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Alias for compatibility
Review = ReviewResponse
