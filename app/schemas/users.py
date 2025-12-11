from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        # Поделаня трансформация пустого email в None
        if v == "" or v is None:
            return None
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    """User schema as it appears in database"""
    password_hash: Optional[str] = None
    
    class Config:
        from_attributes = True

# Alias for compatibility
User = UserResponse
