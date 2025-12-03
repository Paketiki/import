from pydantic import BaseModel
from typing import Optional
from .users import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Response Schemas
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int