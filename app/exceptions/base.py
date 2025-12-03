from fastapi import HTTPException, status

class ObjectAlreadyExistsError(Exception):
    """Исключение, выбрасываемое когда объект уже существует"""
    pass
class MyAppError(Exception):
    """Базовое исключение приложения"""
    pass

class MyAppHTTPError(MyAppError):
    """HTTP-ориентированное исключение"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

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