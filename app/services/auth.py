# app/services/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.schemas.auth import TokenData
from app.exceptions import AuthenticationError
from app.utils.config import settings

class AuthService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if username is None or user_id is None:
                raise AuthenticationError("Invalid token")
            
            return TokenData(username=username, user_id=user_id)
        except JWTError as e:
            raise AuthenticationError(f"Could not validate credentials: {str(e)}")
    
    @staticmethod
    def create_user_token(user_data: dict) -> str:
        """Создать токен для пользователя"""
        token_data = {
            "sub": user_data["username"],
            "user_id": user_data["id"],
            "role": user_data.get("role_name", "Зритель")
        }
        
        if "email" in user_data:
            token_data["email"] = user_data["email"]
        
        return AuthService.create_access_token(token_data)