"""
Глобальные обработчики исключений для FastAPI
"""

import logging
from typing import Any, Dict, Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

from .base import (
    AppException,
    NotFoundException,
    ConflictException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    DatabaseException,
    ServiceUnavailableException,
    RateLimitException,
    IntegrityException,
    BusinessLogicException
)

# Настройка логгера
logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Настройка глобальных обработчиков исключений
    """
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """
        Обработчик пользовательских исключений приложения
        """
        logger.warning(
            f"AppException: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        content: Dict[str, Any] = {
            "message": exc.message,
            "detail": exc.detail
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Обработчик ошибок валидации запросов FastAPI
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type")
            })
        
        logger.warning(
            f"Validation error: {errors}",
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Ошибка валидации запроса",
                "detail": {"errors": errors}
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, 
        exc: ValidationError
    ) -> JSONResponse:
        """
        Обработчик ошибок валидации Pydantic
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type")
            })
        
        logger.warning(
            f"Pydantic validation error: {errors}",
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Ошибка валидации данных",
                "detail": {"errors": errors}
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, 
        exc: IntegrityError
    ) -> JSONResponse:
        """
        Обработчик ошибок целостности базы данных
        """
        logger.error(
            f"Integrity error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception": str(exc)
            },
            exc_info=True
        )
        
        # Пытаемся извлечь информацию об ограничении
        constraint = None
        if exc.orig and hasattr(exc.orig, 'pgcode'):
            # PostgreSQL
            if exc.orig.pgcode == '23505':  # unique_violation
                constraint = "UNIQUE constraint"
            elif exc.orig.pgcode == '23503':  # foreign_key_violation
                constraint = "FOREIGN KEY constraint"
            elif exc.orig.pgcode == '23502':  # not_null_violation
                constraint = "NOT NULL constraint"
        
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Нарушение целостности данных",
                "detail": {
                    "constraint": constraint or "Database constraint",
                    "error": str(exc.orig) if exc.orig else str(exc)
                }
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, 
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """
        Обработчик общих ошибок SQLAlchemy
        """
        logger.error(
            f"SQLAlchemy error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception": str(exc)
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Ошибка базы данных",
                "detail": {
                    "error": str(exc)
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """
        Обработчик всех остальных исключений
        """
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        
        # В production режиме не показываем детали исключения
        import os
        is_production = os.getenv("ENVIRONMENT") == "production"
        
        detail = {}
        if not is_production:
            detail = {
                "error": str(exc),
                "type": exc.__class__.__name__
            }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Внутренняя ошибка сервера",
                "detail": detail
            }
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Обработчик 404 ошибок
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Ресурс не найден",
                "detail": {
                    "path": request.url.path,
                    "method": request.method
                }
            }
        )