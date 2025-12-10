# app/api/picks.py
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/picks", tags=["picks"])

class Pick(BaseModel):
    id: str
    name: str
    slug: str
    description: str = ""

@router.get("/", response_model=List[Pick])
async def get_picks():
    """
    Получить список доступных подборок
    """
    return [
        {"id": "all", "name": "Все фильмы", "slug": "all", "description": "Полная коллекция фильмов"},
        {"id": "hits", "name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
        {"id": "new", "name": "Новинки", "slug": "new", "description": "Новые поступления"},
        {"id": "classic", "name": "Классика", "slug": "classic", "description": "Великие классические фильмы"},
    ]

@router.get("/{pick_slug}", response_model=Pick)
async def get_pick(pick_slug: str):
    """
    Получить информацию о конкретной подборке
    """
    picks = {
        "all": {"id": "all", "name": "Все фильмы", "slug": "all", "description": "Полная коллекция фильмов"},
        "hits": {"id": "hits", "name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
        "new": {"id": "new", "name": "Новинки", "slug": "new", "description": "Новые поступления"},
        "classic": {"id": "classic", "name": "Классика", "slug": "classic", "description": "Великие классические фильмы"},
    }
    
    if pick_slug in picks:
        return picks[pick_slug]
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Подборка не найдена")