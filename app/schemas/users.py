from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import UserRole

class SUserGet(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: str = Field(..., min_length=5)
    role: Optional[UserRole] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=4)

class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=4)
    role: Optional[UserRole] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True