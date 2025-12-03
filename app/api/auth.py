from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.services.users import UserService
from app.services.auth import AuthService
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserInDB
from app.utils.config import settings
from app.utils.dependencies import get_user_service, get_auth_service

router = APIRouter(tags=["kinovzor-auth"])

@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/register", response_model=UserInDB)
async def register(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_user(user_create)