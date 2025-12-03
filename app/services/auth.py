from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.schemas.auth import TokenData
from app.schemas.users import UserRole, UserInDB
from app.exceptions import AuthenticationError
from app.utils.config import settings

class AuthService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            
            if username is None:
                raise AuthenticationError()
            
            return TokenData(username=username, role=UserRole(role) if role else None)
        except JWTError:
            raise AuthenticationError()