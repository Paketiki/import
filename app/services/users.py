from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.repositories.users import UserRepository
from app.schemas.users import UserCreate, UserUpdate, UserInDB
from app.schemas.enums import UserRole
from app.exceptions import UserNotFoundError, DuplicateEntryError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
    
    async def get_user(self, username: str) -> Optional[UserInDB]:
        user = await self.repository.get_by_username(username)
        if not user:
            raise UserNotFoundError(username)
        return UserInDB.from_orm(user)
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[UserInDB]:
        if role:
            users = await self.repository.get_users_by_role(role, skip=skip, limit=limit)
        else:
            users = await self.repository.get_all(skip=skip, limit=limit)
        
        return [UserInDB.from_orm(user) for user in users]
    
    async def create_user(self, user_create: UserCreate) -> UserInDB:
        # Check if user already exists
        existing_user = await self.repository.get_by_username(user_create.username)
        if existing_user:
            raise DuplicateEntryError(f"User {user_create.username} already exists")
        
        # Hash password
        hashed_password = pwd_context.hash(user_create.password)
        
        # Create user dict with only the fields that User model expects
        user_dict = {
            "username": user_create.username,
            "email": user_create.email,
            "password_hash": hashed_password,
            "is_native": False,
        }
        
        user = await self.repository.create(user_dict)
        return UserInDB.from_orm(user)
    
    async def update_user(self, username: str, user_update: UserUpdate) -> UserInDB:
        # Check if user exists
        existing_user = await self.repository.get_by_username(username)
        if not existing_user:
            raise UserNotFoundError(username)
        
        update_data = user_update.dict(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data and update_data["password"]:
            update_data["password"] = pwd_context.hash(update_data["password"])
        
        # Convert role to string if provided
        if "role" in update_data:
            update_data["role"] = update_data["role"].value
        
        user = await self.repository.update(username, update_data)
        if not user:
            raise UserNotFoundError(username)
        
        return UserInDB.from_orm(user)
    
    async def delete_user(self, username: str) -> bool:
        user = await self.repository.get_by_username(username)
        if not user:
            raise UserNotFoundError(username)
        
        return await self.repository.delete(username)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        user = await self.repository.get_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return UserInDB.from_orm(user)