from fastapi import APIRouter, Depends, Query
from typing import List

from app.schemas.picks import PickCreate, PickInDB
from app.services.picks import PickService
from app.api.dependencies import get_current_admin_user
from app.utils.dependencies import get_pick_service

# Убираем prefix из роутера
router = APIRouter(tags=["picks"])

@router.get("/picks", response_model=List[PickInDB])
async def read_picks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    pick_service: PickService = Depends(get_pick_service),
):
    return await pick_service.get_picks(skip=skip, limit=limit)

@router.get("/picks/{pick_id}", response_model=PickInDB)
async def read_pick(
    pick_id: int,
    pick_service: PickService = Depends(get_pick_service),
):
    return await pick_service.get_pick(pick_id)

@router.get("/picks/name/{name}", response_model=PickInDB)
async def read_pick_by_name(
    name: str,
    pick_service: PickService = Depends(get_pick_service),
):
    return await pick_service.get_pick_by_name(name)

@router.post("/picks", response_model=PickInDB)
async def create_pick(
    pick: PickCreate,
    current_user = Depends(get_current_admin_user),
    pick_service: PickService = Depends(get_pick_service),
):
    return await pick_service.create_pick(pick)

@router.put("/picks/{pick_id}", response_model=PickInDB)
async def update_pick(
    pick_id: int,
    pick_update: PickCreate,
    current_user = Depends(get_current_admin_user),
    pick_service: PickService = Depends(get_pick_service),
):
    return await pick_service.update_pick(pick_id, pick_update)

@router.delete("/picks/{pick_id}")
async def delete_pick(
    pick_id: int,
    current_user = Depends(get_current_admin_user),
    pick_service: PickService = Depends(get_pick_service),
):
    await pick_service.delete_pick(pick_id)
    return {"message": "Pick deleted successfully"}