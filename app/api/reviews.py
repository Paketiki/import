from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.schemas.reviews import ReviewCreate, ReviewUpdate, ReviewInDB
from app.services.reviews import ReviewService
from app.api.dependencies import get_current_user
from app.utils.dependencies import get_review_service

# Убираем prefix из роутера
router = APIRouter(tags=["reviews"])

@router.get("/reviews", response_model=List[ReviewInDB])
async def read_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    movie_id: Optional[int] = Query(None),
    username: Optional[str] = Query(None),
    review_service: ReviewService = Depends(get_review_service),
    current_user = Depends(get_current_user),
):
    if movie_id:
        return await review_service.get_reviews_by_movie(movie_id, skip, limit)
    elif username:
        # Users can only view their own reviews unless they're admin
        if username != current_user.username and current_user.role.value != "admin":
            from app.exceptions import InsufficientPermissionsError
            raise InsufficientPermissionsError()
        
        return await review_service.get_reviews_by_user(username, skip, limit)
    else:
        from app.exceptions import ValidationError
        raise ValidationError("Must specify either movie_id or username")

@router.get("/reviews/{review_id}", response_model=ReviewInDB)
async def read_review(
    review_id: int,
    current_user = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    review = await review_service.get_review(review_id)
    
    # Users can only view their own reviews unless they're admin
    if review.username != current_user.username and current_user.role.value != "admin":
        from app.exceptions import InsufficientPermissionsError
        raise InsufficientPermissionsError()
    
    return review

@router.post("/reviews", response_model=ReviewInDB)
async def create_review(
    review: ReviewCreate,
    current_user = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.create_review(review, current_user.username)

@router.put("/reviews/{review_id}", response_model=ReviewInDB)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    review = await review_service.get_review(review_id)
    
    # Users can only update their own reviews unless they're admin
    if review.username != current_user.username and current_user.role.value != "admin":
        from app.exceptions import InsufficientPermissionsError
        raise InsufficientPermissionsError()
    
    return await review_service.update_review(review_id, review_update)

@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: int,
    current_user = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    review = await review_service.get_review(review_id)
    
    # Users can only delete their own reviews unless they're admin
    if review.username != current_user.username and current_user.role.value != "admin":
        from app.exceptions import InsufficientPermissionsError
        raise InsufficientPermissionsError()
    
    await review_service.delete_review(review_id)
    return {"message": "Review deleted successfully"}