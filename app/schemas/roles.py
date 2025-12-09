from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RoleInDB(Role):
    pass

# Добавить для совместимости
SRoleGet = Role  # Псевдоним для relations_users_roles.py