# app/services/users.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.users import User
from app.models.roles import Role
from app.schemas.users import UserCreate, UserUpdate, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id).options(
            select(User.role)  # Eager load role
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username).options(
            select(User.role)  # Eager load role
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_users(self, skip: int = 0, limit: int = 100, 
                       search: Optional[str] = None, 
                       role_name: Optional[str] = None) -> List[User]:
        stmt = select(User).options(select(User.role))
        
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(User.username.ilike(search_term))
        
        if role_name:
            stmt = stmt.join(User.role).where(Role.name == role_name)
        
        stmt = stmt.offset(skip).limit(limit).order_by(User.username)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create_user(self, user_data: UserCreate) -> User:
        # Находим роль "Зритель" по умолчанию
        role_stmt = select(Role).where(Role.name == "Зритель")
        role_result = await self.db.execute(role_stmt)
        role = role_result.scalar_one_or_none()
        
        if not role:
            # Создаем роль если не существует
            role = Role(name="Зритель", description="Обычный пользователь")
            self.db.add(role)
            await self.db.flush()
        
        # Хэшируем пароль
        hashed_password = pwd_context.hash(user_data.password)
        
        # Создаем пользователя
        user = User(
            username=user_data.username,
            email=user_data.email if user_data.email else f"{user_data.username}@example.com",
            password_hash=hashed_password,
            role_id=role.id,
            is_native=False
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        # Обрабатываем пароль отдельно
        if 'password' in update_data:
            hashed_password = pwd_context.hash(update_data['password'])
            user.password_hash = hashed_password
            del update_data['password']
        
        # Обрабатываем роль
        if 'role_id' in update_data:
            user.role_id = update_data['role_id']
            del update_data['role_id']
        
        # Обновляем остальные поля
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        
        return False
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.get_user_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user