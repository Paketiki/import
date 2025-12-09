# app/services/__init__.py
from .auth import AuthService
from .users import UserService
from .movies import MovieService
from .reviews import ReviewService
from .roles import RoleService
from .picks import PickService
from .movie_loader import MovieLoader
from .movie_picks import MoviePickService
from .movie_stats import MovieStatService
from .base import BaseService

__all__ = [
    "AuthService",
    "UserService",
    "MovieService",
    "ReviewService", 
    "RoleService",
    "PickService",
    "MovieLoader",
    "MoviePickService",
    "MovieStatService",
    "BaseService"
]