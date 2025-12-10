# app/api/sample.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/sample")
async def sample_endpoint():
    return {"message": "Это sample endpoint"}