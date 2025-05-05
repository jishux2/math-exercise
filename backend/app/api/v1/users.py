from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...services import UserService
from ...schemas import user as schemas
from ...models import User
from ..deps import (
    get_current_active_user,
    check_teacher,
    check_parent,
    check_admin
)

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

@router.post("/teachers", response_model=schemas.UserResponse)
def create_teacher(
    *,
    db: Session = Depends(get_db),
    teacher_in: schemas.TeacherCreate,
) -> Any:
    """创建教师账号"""
    user_service = UserService(db)
    return user_service.create_teacher(teacher_in)

@router.post("/parents", response_model=schemas.UserResponse)
def create_parent(
    *,
    db: Session = Depends(get_db),
    parent_in: schemas.ParentCreate,
) -> Any:
    """创建家长账号"""
    user_service = UserService(db)
    return user_service.create_parent(parent_in)

@router.get("/teachers/students", response_model=List[schemas.UserResponse])
def get_teacher_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher),
) -> Any:
    """获取教师的学生列表"""
    user_service = UserService(db)
    return user_service.get_teacher_students(current_user.id)

@router.get("/parents/students", response_model=List[schemas.UserResponse])
def get_parent_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_parent),
) -> Any:
    """获取家长关联的学生列表"""
    user_service = UserService(db)
    return user_service.get_parent_students(current_user.id)

@router.post("/students/{student_id}/teacher", response_model=schemas.UserResponse)
def assign_teacher(
    student_id: int,
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin),
) -> Any:
    """为学生分配教师"""
    user_service = UserService(db)
    return user_service.assign_teacher(student_id, teacher_id)

@router.post("/students/{student_id}/parent", response_model=schemas.UserResponse)
def link_parent(
    student_id: int,
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin),
) -> Any:
    """关联学生和家长"""
    user_service = UserService(db)
    return user_service.link_parent(student_id, parent_id)