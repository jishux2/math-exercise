from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import User, Exercise
from ..schemas import user as schemas
from ..core.security import get_password_hash, verify_password
from .base import BaseService


class UserService(BaseService[User, schemas.UserCreate, schemas.UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, *, obj_in: schemas.UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password)
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: User, obj_in: schemas.UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db_obj=db_obj, obj_in=schemas.UserUpdate(**update_data))

    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_stats(self, user_id: int) -> dict:
        """获取用户的练习统计信息"""
        stats = self.db.query(
            func.count(Exercise.id).label('total_exercises'),
            func.avg(Exercise.final_score).label('average_score'),
            func.sum(Exercise.total_time).label('total_time')
        ).filter(Exercise.user_id == user_id).first()

        completed_exercises = self.db.query(
            func.count(Exercise.id)
        ).filter(
            Exercise.user_id == user_id,
            Exercise.completed_at.isnot(None)
        ).scalar()

        return {
            "total_exercises": stats[0] or 0,
            "completed_exercises": completed_exercises or 0,
            "average_score": round(stats[1] or 0, 2),
            "total_time": stats[2] or 0
        }