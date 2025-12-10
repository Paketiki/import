# app/schemas/__init__.py
from .auth import Token, TokenData
from .movies import (
    MovieBase, MovieCreate, MovieUpdate, 
    MovieResponse, MovieDetailResponse
)
from .reviews import ReviewBase, ReviewCreate, ReviewResponse, ReviewUpdate
from .users import UserBase, UserCreate, UserResponse, UserUpdate
from .roles import RoleBase, RoleCreate, RoleResponse
from .picks import PickBase, PickCreate, PickResponse

__all__ = [
    "Token",
    "TokenData",
    "UserBase",
    "UserCreate",
    "UserResponse", 
    "UserUpdate",
    "MovieBase",
    "MovieCreate",
    "MovieUpdate",
    "MovieResponse",
    "MovieDetailResponse",
    "ReviewBase",
    "ReviewCreate",
    "ReviewResponse",
    "ReviewUpdate",
    "RoleBase",
    "RoleCreate",
    "RoleResponse",
    "PickBase",
    "PickCreate",
    "PickResponse",
]