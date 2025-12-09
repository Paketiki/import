from .auth import *
from .base import *
from .movies import *
from app.exceptions.base import ObjectAlreadyExistsError
from .handlers import setup_exception_handlers


class NotFoundError(Exception):
    def __init__(self, message: str = "Объект не найден"):
        self.message = message
        super().__init__(self.message)

class ConflictError(Exception):
    def __init__(self, message: str = "Конфликт данных"):
        self.message = message
        super().__init__(self.message)

class ValidationError(Exception):
    def __init__(self, message: str = "Ошибка валидации"):
        self.message = message
        super().__init__(self.message)

        
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