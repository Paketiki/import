# app/models/__init__.py
from .base import Base
from .users import User
from .movies import Movie
from .reviews import Review
from .picks import Pick
# Временно удалите остальные импорты если есть проблемы

__all__ = ["Base", "User", "Movie", "Review", "Pick"]