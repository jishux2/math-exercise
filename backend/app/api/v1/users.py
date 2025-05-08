from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...services import UserService
from ...schemas import user as schemas
from ...models import User, UserRole
from ..deps import (
    get_current_active_user,
    check_teacher,
    check_parent,
    check_admin,
    check_teacher_or_admin,
    check_parent_or_admin
)

router = APIRouter()

@router.post("/students", response_model=schemas.UserResponse)
def create_student(
    *,
    db: Session = Depends(get_db),
    student_in: schemas.StudentCreate
) -> Any:
    """创建学生账号"""
    user_service = UserService(db)
    if user_service.get_by_email(email=student_in.email):
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册"
        )
    return user_service.create_student(obj_in=student_in)

@router.post("/teachers", response_model=schemas.UserResponse)
def create_teacher(
    *,
    db: Session = Depends(get_db),
    teacher_in: schemas.TeacherCreate,
    current_user: User = Depends(check_admin)  # 只有管理员可以创建教师账号
) -> Any:
    """创建教师账号"""
    user_service = UserService(db)
    if user_service.get_by_email(email=teacher_in.email):
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册"
        )
    return user_service.create_teacher(obj_in=teacher_in)

@router.post("/parents", response_model=schemas.UserResponse)
def create_parent(
    *,
    db: Session = Depends(get_db),
    parent_in: schemas.ParentCreate,
    current_user: User = Depends(check_admin)  # 只有管理员可以创建家长账号
) -> Any:
    """创建家长账号"""
    user_service = UserService(db)
    if user_service.get_by_email(email=parent_in.email):
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册"
        )
    return user_service.create_parent(obj_in=parent_in)

@router.get("/me", response_model=schemas.UserResponse)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户信息"""
    response = {**current_user.__dict__}
    
    # 根据角色添加profile信息
    if current_user.role == UserRole.STUDENT and current_user.student:
        response["student_profile"] = schemas.StudentProfile(
            grade=current_user.student.grade,
            class_name=current_user.student.class_name
        )
    elif current_user.role == UserRole.TEACHER and current_user.teacher:
        response["teacher_profile"] = schemas.TeacherProfile(
            subjects=current_user.teacher.subjects
        )
        
    return response

@router.put("/me", response_model=schemas.UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新当前用户信息"""
    user_service = UserService(db)
    
    # 如果要更新邮箱，检查新邮箱是否已被使用
    if user_in.email and user_in.email != current_user.email:
        if user_service.get_by_email(email=user_in.email):
            raise HTTPException(
                status_code=400,
                detail="该邮箱已被其他用户使用"
            )
    
    return user_service.update(db_obj=current_user, obj_in=user_in)

@router.get("/students", response_model=List[schemas.UserResponse])
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher_or_admin)
) -> Any:
    """获取学生列表（仅教师和管理员可访问）"""
    user_service = UserService(db)
    if current_user.role == UserRole.TEACHER:
        return user_service.get_teacher_students(current_user.teacher.id)
    return user_service.get_all_students()

@router.get("/teachers/{teacher_id}/students", response_model=List[schemas.UserResponse])
def get_teacher_students(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_teacher_or_admin)
) -> Any:
    """获取指定教师的学生列表"""
    if current_user.role == UserRole.TEACHER and current_user.teacher.id != teacher_id:
        raise HTTPException(
            status_code=403,
            detail="只能查看自己的学生列表"
        )
    user_service = UserService(db)
    return user_service.get_teacher_students(teacher_id)

@router.get("/parents/{parent_id}/students", response_model=List[schemas.UserResponse])
def get_parent_students(
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_parent_or_admin)
) -> Any:
    """获取指定家长关联的学生列表"""
    if current_user.role == UserRole.PARENT and current_user.parent.id != parent_id:
        raise HTTPException(
            status_code=403,
            detail="只能查看自己关联的学生列表"
        )
    user_service = UserService(db)
    return user_service.get_parent_students(parent_id)

@router.post("/students/{student_id}/teacher/{teacher_id}")
def assign_teacher(
    student_id: int,
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
) -> Any:
    """为学生分配教师（仅管理员可操作）"""
    user_service = UserService(db)
    if not user_service.assign_teacher(student_id, teacher_id):
        raise HTTPException(
            status_code=400,
            detail="分配失败，请检查学生和教师ID是否正确"
        )
    return {"success": True}

@router.post("/students/{student_id}/parent/{parent_id}")
def link_parent(
    student_id: int,
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
) -> Any:
    """关联学生和家长（仅管理员可操作）"""
    user_service = UserService(db)
    if not user_service.link_parent(student_id, parent_id):
        raise HTTPException(
            status_code=400,
            detail="关联失败，请检查学生和家长ID是否正确"
        )
    return {"success": True}

@router.get("/students/{student_id}/progress", response_model=schemas.StudentProgress)
def get_student_progress(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取学生学习进度
    教师可以查看自己的学生
    家长可以查看自己关联的学生
    管理员可以查看所有学生
    """
    # 检查权限
    if current_user.role == UserRole.STUDENT:
        if current_user.student.id != student_id:
            raise HTTPException(status_code=403, detail="只能查看自己的学习进度")
    elif current_user.role == UserRole.TEACHER:
        if student_id not in [s.id for s in current_user.teacher.students]:
            raise HTTPException(status_code=403, detail="只能查看自己的学生")
    elif current_user.role == UserRole.PARENT:
        if student_id not in [s.id for s in current_user.parent.students]:
            raise HTTPException(status_code=403, detail="只能查看自己关联的学生")
    
    user_service = UserService(db)
    return user_service.get_student_progress(student_id)