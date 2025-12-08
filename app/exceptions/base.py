from fastapi import HTTPException, status
from typing import Optional, Any, Dict

class ObjectAlreadyExistsError(Exception):
    """Исключение, выбрасываемое когда объект уже существует"""
    pass
class MyAppError(Exception):
    """Базовое исключение приложения"""
    pass

class MyAppHTTPError(HTTPException):
    """Базовый класс для HTTP ошибок"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundError(BaseAPIException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class DuplicateEntryError(BaseAPIException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ValidationError(BaseAPIException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class AppException(Exception):
    """Базовое исключение приложения"""
    
    def __init__(
        self,
        message: str = "Произошла ошибка",
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        self.headers = headers
        super().__init__(self.message)


class NotFoundException(AppException):
    """Исключение для случаев, когда ресурс не найден"""
    
    def __init__(
        self,
        message: str = "Ресурс не найден",
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            status_code=404,
            detail=detail,
            headers=headers
        )


class ConflictException(AppException):
    """Исключение для конфликтных ситуаций (например, дублирование данных)"""
    
    def __init__(
        self,
        message: str = "Конфликт данных",
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            status_code=409,
            detail=detail,
            headers=headers
        )


class BadRequestException(AppException):
    """Исключение для некорректных запросов"""
    
    def __init__(
        self,
        message: str = "Некорректный запрос",
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            detail=detail,
            headers=headers
        )


class UnauthorizedException(AppException):
    """Исключение для случаев, когда требуется авторизация"""
    
    def __init__(
        self,
        message: str = "Требуется авторизация",
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            status_code=401,
            detail=detail,
            headers=headers
        )


class ForbiddenException(AppException):
    """Исключение для случаев, когда доступ запрещен"""
    
    def __init__(
        self,
        message: str = "Доступ запрещен",
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            detail=detail,
            headers=headers
        )


class ValidationException(AppException):
    """Исключение для ошибок валидации"""
    
    def __init__(
        self,
        message: str = "Ошибка валидации",
        errors: Optional[Dict[str, Any]] = None,
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        full_detail = detail or {}
        if errors:
            full_detail["errors"] = errors
        
        super().__init__(
            message=message,
            status_code=422,
            detail=full_detail,
            headers=headers
        )


class DatabaseException(AppException):
    """Исключение для ошибок базы данных"""
    
    def __init__(
        self,
        message: str = "Ошибка базы данных",
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            detail=detail,
            headers=headers
        )


class ServiceUnavailableException(AppException):
    """Исключение для случаев, когда сервис недоступен"""
    
    def __init__(
        self,
        message: str = "Сервис временно недоступен",
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            status_code=503,
            detail=detail,
            headers=headers
        )


class RateLimitException(AppException):
    """Исключение для случаев превышения лимита запросов"""
    
    def __init__(
        self,
        message: str = "Превышен лимит запросов",
        retry_after: Optional[int] = None,
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        if headers is None:
            headers = {}
        
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            message=message,
            status_code=429,
            detail=detail,
            headers=headers
        )


class IntegrityException(DatabaseException):
    """Исключение для нарушений целостности данных в БД"""
    
    def __init__(
        self,
        message: str = "Нарушение целостности данных",
        constraint: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        full_detail = detail or {}
        if constraint:
            full_detail["constraint"] = constraint
        
        super().__init__(
            message=message,
            detail=full_detail,
            headers=headers
        )


class BusinessLogicException(AppException):
    """Исключение для нарушений бизнес-логики"""
    
    def __init__(
        self,
        message: str = "Нарушение бизнес-логики",
        code: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        full_detail = detail or {}
        if code:
            full_detail["code"] = code
        
        super().__init__(
            message=message,
            status_code=400,
            detail=full_detail,
            headers=headers
        )