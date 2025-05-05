from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import User, Student, Exercise, UserRole
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
    
    def create_teacher(self, teacher_in: schemas.TeacherCreate) -> User:
        """创建教师账号"""
        user = self.create(obj_in=teacher_in)
        # 可以添加教师特有的初始化逻辑
        return user

    def create_parent(self, parent_in: schemas.ParentCreate) -> User:
        """创建家长账号"""
        user = self.create(obj_in=parent_in)
        # 处理学生关联
        for email in parent_in.student_emails:
            student = self.get_by_email(email)
            if student and student.role == UserRole.STUDENT:
                student_info = self.db.query(Student).filter(
                    Student.user_id == student.id
                ).first()
                if student_info:
                    student_info.parent_id = user.id
        self.db.commit()
        return user

    def get_teacher_students(self, teacher_id: int) -> List[User]:
        """获取教师的学生列表"""
        students = self.db.query(Student).filter(
            Student.teacher_id == teacher_id
        ).all()
        return [s.user for s in students]

    def get_parent_students(self, parent_id: int) -> List[User]:
        """获取家长关联的学生列表"""
        students = self.db.query(Student).filter(
            Student.parent_id == parent_id
        ).all()
        return [s.user for s in students]

    def assign_teacher(self, student_id: int, teacher_id: int) -> User:
        """为学生分配教师"""
        student = self.db.query(Student).filter(
            Student.user_id == student_id
        ).first()
        if not student:
            raise ValueError("Student not found")
            
        teacher = self.get(teacher_id)
        if not teacher or teacher.role != UserRole.TEACHER:
            raise ValueError("Invalid teacher")
            
        student.teacher_id = teacher_id
        self.db.commit()
        return student.user

    def link_parent(self, student_id: int, parent_id: int) -> User:
        """关联学生和家长"""
        student = self.db.query(Student).filter(
            Student.user_id == student_id
        ).first()
        if not student:
            raise ValueError("Student not found")
            
        parent = self.get(parent_id)
        if not parent or parent.role != UserRole.PARENT:
            raise ValueError("Invalid parent")
            
        student.parent_id = parent_id
        self.db.commit()
        return student.user

    def create(self, *, obj_in: schemas.UserCreate) -> User:
        """创建用户，同时处理学生信息"""
        # 从obj_in创建数据字典，但不包含password字段
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            role=getattr(obj_in, 'role', UserRole.STUDENT),  # 默认为学生角色
            is_active=True
        )
        self.db.add(db_obj)
        
        # 如果是学生且提供了学生信息，创建学生记录
        if db_obj.role == UserRole.STUDENT and hasattr(obj_in, 'student_info') and obj_in.student_info:
            student = Student(
                user_id=db_obj.id,
                grade=obj_in.student_info.grade,
                class_name=obj_in.student_info.class_name
            )
            self.db.add(student)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj