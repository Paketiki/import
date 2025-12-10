# app/services/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.database.database import get_db
from app.models import User, Role
from app.schemas import UserCreate, TokenData

# Настройки для JWT
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Функции хелперы (оставляем как есть)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_user(db: Session, user_data: UserCreate):
    # Хэшируем пароль
    hashed_password = get_password_hash(user_data.password)
    
    # Получаем роль "Зритель"
    viewer_role = db.query(Role).filter(Role.name == "Зритель").first()
    if not viewer_role:
        # Создаем роль если её нет
        viewer_role = Role(name="Зритель", description="Обычный пользователь")
        db.add(viewer_role)
        db.commit()
        db.refresh(viewer_role)
    
    # Создаем пользователя
    db_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


# Класс AuthService
class AuthService:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return verify_password(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password):
        return get_password_hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        return create_access_token(data, expires_delta)
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        return authenticate_user(db, username, password)
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate):
        return create_user(db, user_data)
    
    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        return get_current_user(token, db)