# app/schemas/users.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .enums import UserRole
from .roles import Role  # Импортируем Role для отношений

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
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ДОБАВЛЯЕМ ЭТОТ КЛАСС
class UserResponse(UserInDB):
    """Схема для ответа API с информацией о пользователе"""
    role_details: Optional[Role] = None  # Детали роли если нужны

# Для обратной совместимости
User = UserInDB