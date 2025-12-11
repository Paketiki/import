from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.schemas import Token, UserCreate, UserResponse
from app.models import User
from app.utils.security import (
    create_access_token, 
    verify_password, 
    get_password_hash
)

router = APIRouter()

class LoginRequest(BaseModel):
    """Схема для запроса логина"""
    username: str
    password: str

@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Вход в систему"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверяем существование пользователя
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    
    # Проверяем email
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email or "",
        password_hash=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем токен
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    """Выход из системы"""
    return {"message": "Успешный выход из системы"}
