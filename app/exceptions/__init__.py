from .auth import *
from .base import *
from .movies import *
from app.exceptions.base import ObjectAlreadyExistsError
from .handlers import setup_exception_handlers

__all__ = [
    'AppException',
    'NotFoundException',
    'ConflictException',
    'BadRequestException',
    'UnauthorizedException',
    'ForbiddenException',
    'ValidationException',
    'DatabaseException',
    'ServiceUnavailableException',
    'RateLimitException',
    'IntegrityException',
    'BusinessLogicException',
    'setup_exception_handlers',
    "AuthenticationError",
    "ObjectAlreadyExistsError",
    "InsufficientPermissionsError",
    "UserNotFoundError",
    "MovieNotFoundError",
    "ReviewNotFoundError",
    "PickNotFoundError",
    "DuplicateEntryError",
    "ValidationError",
]