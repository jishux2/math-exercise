from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...services import UserService
from ...schemas import user as schemas
from ...models import User
from ..deps import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
) -> Any:
    user_service = UserService(db)
    user = user_service.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists."
        )
    user = user_service.create(obj_in=user_in)
    return user

@router.get("/me", response_model=schemas.UserResponse)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    user_service = UserService(db)
    stats = user_service.get_user_stats(current_user.id)
    return {
        **current_user.__dict__,
        "exercise_count": stats["total_exercises"],
        "average_score": stats["average_score"]
    }

@router.put("/me", response_model=schemas.UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    user_service = UserService(db)
    user = user_service.update(db_obj=current_user, obj_in=user_in)
    return user

@router.get("/me/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    user_service = UserService(db)
    return user_service.get_user_stats(current_user.id)