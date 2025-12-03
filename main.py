import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.config import settings
from app.database.db_manager import init_db

# Импорт роутеров
from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as roles_router
from app.api.movies import router as movies_router
from app.api.reviews import router as reviews_router
from app.api.users import router as users_router
from app.api.picks import router as picks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения
    """
    # Startup логика
    print("Starting KinoVzor API...")
    
    # Инициализация базы данных
    try:
        await init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise
    
    print("✓ Application started successfully")
    print(f"✓ API Documentation: http://localhost:8000{settings.api_prefix}/docs")
    print(f"✓ ReDoc Documentation: http://localhost:8000{settings.api_prefix}/redoc")
    
    yield
    
    # Shutdown логика
    print("Shutting down KinoVzor API...")

# Создание приложения FastAPI
app = FastAPI(
    title=settings.project_name,
    description="API для кинопортала KinoVzor с управлением пользователями, фильмами, рецензиями и категориями",
    version=settings.project_version,
    contact={
        "name": "KinoVzor Team",
        "url": "https://github.com/username/kinovzor",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    lifespan=lifespan,
)

# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Включение роутеров
app.include_router(sample_router, tags=["sample"])
app.include_router(auth_router, tags=["authentication"], prefix=settings.api_prefix)
app.include_router(roles_router, tags=["roles"], prefix=settings.api_prefix)
app.include_router(movies_router, tags=["movies"], prefix=settings.api_prefix)
app.include_router(reviews_router, tags=["reviews"], prefix=settings.api_prefix)
app.include_router(users_router, tags=["users"], prefix=settings.api_prefix)
app.include_router(picks_router, tags=["picks"], prefix=settings.api_prefix)

# Глобальные обработчики ошибок
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"detail": "Ресурс не найден"},
    )

@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )

# Конечные точки для мониторинга и управления
@app.get("/", include_in_schema=False)
async def root():
    """
    Корневой эндпоинт с информацией о API
    """
    return {
        "app": settings.project_name,
        "version": settings.project_version,
        "status": "running",
        "documentation": {
            "swagger": f"{settings.api_prefix}/docs",
            "redoc": f"{settings.api_prefix}/redoc",
            "openapi": f"{settings.api_prefix}/openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "api_base": settings.api_prefix,
            "auth": f"{settings.api_prefix}/auth",
            "movies": f"{settings.api_prefix}/movies",
            "reviews": f"{settings.api_prefix}/reviews",
            "users": f"{settings.api_prefix}/users",
            "roles": f"{settings.api_prefix}/roles",
            "picks": f"{settings.api_prefix}/picks",
        }
    }

@app.get("/health", tags=["monitoring"])
async def health_check():
    """
    Проверка состояния приложения
    """
    from datetime import datetime
    import psutil
    import os
    
    # Базовая информация о системе
    system_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": settings.project_name,
        "version": settings.project_version,
        "environment": "development" if settings.debug else "production",
    }
    
    # Информация о памяти
    try:
        memory = psutil.virtual_memory()
        system_info["memory"] = {
            "total": f"{memory.total // (1024**2)} MB",
            "available": f"{memory.available // (1024**2)} MB",
            "percent": f"{memory.percent}%",
        }
    except:
        system_info["memory"] = "N/A"
    
    # Информация о CPU
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        system_info["cpu"] = {
            "percent": f"{cpu_percent}%",
            "cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
        }
    except:
        system_info["cpu"] = "N/A"
    
    # Информация о диске
    try:
        disk = psutil.disk_usage('/')
        system_info["disk"] = {
            "total": f"{disk.total // (1024**3)} GB",
            "free": f"{disk.free // (1024**3)} GB",
            "percent": f"{disk.percent}%",
        }
    except:
        system_info["disk"] = "N/A"
    
    return system_info

@app.get("/info", tags=["monitoring"], include_in_schema=False)
async def app_info():
    """
    Подробная информация о приложении
    """
    import sys
    import platform
    
    return {
        "app": {
            "name": settings.project_name,
            "version": settings.project_version,
            "debug": settings.debug,
            "api_prefix": settings.api_prefix,
        },
        "python": {
            "version": sys.version,
            "implementation": platform.python_implementation(),
        },
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "database": {
            "url": "configured" if settings.database_url else "not configured",
            "type": "sqlite" if "sqlite" in settings.database_url else "postgresql",
        },
        "security": {
            "jwt_algorithm": settings.algorithm,
            "token_expire_minutes": settings.access_token_expire_minutes,
        }
    }

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=True,
    )