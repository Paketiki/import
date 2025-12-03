from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Hello from sample router"}

@router.get("/items/{item_id}")
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    return {"item_id": item_id, "db": "connected"}