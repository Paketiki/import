from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from app.database.database import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth import AuthService
from app.services.users import UserService
from app.schemas.users import UserInDB
from app.schemas.enums import UserRole
from app.exceptions import AuthenticationError, InsufficientPermissionsError
from app.utils.dependencies import get_user_service, get_auth_service

# Create a custom OAuth2 scheme that doesn't show in Swagger UI
class NoAuthOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl=tokenUrl, auto_error=False)

oauth2_scheme = NoAuthOAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> UserInDB:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token_data = auth_service.verify_token(token)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_service.get_user(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    return current_user

async def get_current_admin_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    if current_user.role != UserRole.ADMIN:
        raise InsufficientPermissionsError()
    return current_user

DBDep = Annotated[AsyncSession, Depends(get_db)]