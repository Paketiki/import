# app/api/picks.py
from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.picks import Pick as PickModel

router = APIRouter(prefix="/picks", tags=["picks"])

class Pick(BaseModel):
    id: int
    name: str
    slug: str
    description: str = ""
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[Pick])
async def get_picks(db: Session = Depends(get_db)):
    """
    Получить список доступных подборок из БД
    """
    picks = db.query(PickModel).all()
    
    # Если в БД нет подборок, создаем стандартные
    if not picks:
        default_picks = [
            {"id": 1, "name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
            {"id": 2, "name": "Новинки", "slug": "new", "description": "Новые поступления"},
            {"id": 3, "name": "Классика", "slug": "classic", "description": "Великие классические фильмы"},
        ]
        
        for pick_data in default_picks:
            pick = PickModel(**pick_data)
            db.add(pick)
        db.commit()
        
        # Загружаем созданные подборки
        picks = db.query(PickModel).all()
    
    return picks

@router.get("/{pick_slug}", response_model=Pick)
async def get_pick(pick_slug: str, db: Session = Depends(get_db)):
    """
    Получить информацию о конкретной подборке
    """
    pick = db.query(PickModel).filter(PickModel.slug == pick_slug).first()
    if not pick:
        # Ищем в стандартных подборках
        default_picks = {
            "all": {"id": 0, "name": "Все фильмы", "slug": "all", "description": "Полная коллекция фильмов"},
            "hits": {"id": 1, "name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
            "new": {"id": 2, "name": "Новинки", "slug": "new", "description": "Новые поступления"},
            "classic": {"id": 3, "name": "Классика", "slug": "classic", "description": "Великие классические фильмы"},
        }
        
        if pick_slug in default_picks:
            return default_picks[pick_slug]
        
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Подборка не найдена")
    
    return pick