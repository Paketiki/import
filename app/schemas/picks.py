from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PickBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)

class PickCreate(PickBase):
    pass

class PickUpdate(PickBase):
    pass

class PickInDB(PickBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Для обратной совместимости
Pick = PickInDB