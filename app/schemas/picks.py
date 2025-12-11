from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PickBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class PickCreate(PickBase):
    created_by: Optional[int] = None

class PickResponse(PickBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PickInDB(PickResponse):
    """Pick schema as it appears in database (alias for compatibility)"""
    class Config:
        from_attributes = True
