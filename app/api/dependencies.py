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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> UserInDB:
    try:
        token_data = auth_service.verify_token(token)
    except AuthenticationError:
        raise AuthenticationError()
    
    user = await user_service.get_user(token_data.username)
    if user is None:
        raise AuthenticationError()
    
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