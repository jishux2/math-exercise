from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import User, Student, Teacher, Parent, Exercise, UserRole
from ..schemas import user as schemas
from ..core.security import get_password_hash, verify_password
from .base import BaseService


class UserService(BaseService[User, schemas.UserCreateBase, schemas.UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_student(self, *, obj_in: schemas.StudentCreate) -> User:
        """创建学生用户"""
        # 创建基础用户
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            role=UserRole.STUDENT
        )
        self.db.add(db_obj)
        self.db.flush()  # 获取user.id

        # 创建学生信息
        student = Student(
            user_id=db_obj.id,
            grade=obj_in.profile.grade,
            class_name=obj_in.profile.class_name
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_teacher(self, *, obj_in: schemas.TeacherCreate) -> User:
        """创建教师用户"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            role=UserRole.TEACHER
        )
        self.db.add(db_obj)
        self.db.flush()

        teacher = Teacher(
            user_id=db_obj.id,
            subjects=obj_in.profile.subjects
        )
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_parent(self, *, obj_in: schemas.ParentCreate) -> User:
        """创建家长用户"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            role=UserRole.PARENT
        )
        self.db.add(db_obj)
        self.db.flush()

        parent = Parent(user_id=db_obj.id)
        self.db.add(parent)

        # 处理学生关联
        for email in obj_in.student_emails:
            student_user = self.get_by_email(email)
            if student_user and student_user.role == UserRole.STUDENT:
                student = student_user.student
                if student:
                    student.parent_id = parent.id

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: User, obj_in: schemas.UserUpdate) -> User:
        """更新用户信息"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 处理密码更新
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        # 根据角色更新特定信息
        if db_obj.role == UserRole.STUDENT and hasattr(obj_in, 'profile'):
            profile = update_data.pop('profile', None)
            if profile and db_obj.student:
                for key, value in profile.items():
                    setattr(db_obj.student, key, value)

        return super().update(db_obj=db_obj, obj_in=schemas.UserUpdate(**update_data))

    def get_student_stats(self, student_id: int) -> Dict[str, Any]:
        """获取学生的练习统计信息"""
        stats = self.db.query(
            func.count(Exercise.id).label('total_exercises'),
            func.count(Exercise.completed_at).label('completed_exercises'),
            func.avg(Exercise.final_score).label('average_score'),
            func.sum(Exercise.total_time).label('total_time')
        ).filter(
            Exercise.student_id == student_id
        ).first()

        return {
            "total_exercises": stats[0] or 0,
            "completed_exercises": stats[1] or 0,
            "average_score": round(stats[2] or 0, 2),
            "total_time": stats[3] or 0
        }

    def get_teacher_students(self, teacher_id: int) -> List[User]:
        """获取教师的学生列表"""
        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            return []
        return [student.user for student in teacher.students]

    def get_parent_students(self, parent_id: int) -> List[User]:
        """获取家长关联的学生列表"""
        parent = self.db.query(Parent).filter(Parent.id == parent_id).first()
        if not parent:
            return []
        return [student.user for student in parent.students]

    def assign_teacher(self, student_id: int, teacher_id: int) -> bool:
        """分配教师给学生"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        
        if not student or not teacher:
            return False
            
        student.teacher_id = teacher.id
        self.db.commit()
        return True

    def link_parent(self, student_id: int, parent_id: int) -> bool:
        """关联学生和家长"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        parent = self.db.query(Parent).filter(Parent.id == parent_id).first()
        
        if not student or not parent:
            return False
            
        student.parent_id = parent.id
        self.db.commit()
        return True

    def get_all_students(self) -> List[User]:
        """获取所有学生（仅管理员使用）"""
        return self.db.query(User).filter(User.role == UserRole.STUDENT).all()

    def get_student_progress(self, student_id: int) -> Dict[str, Any]:
        """获取学生的学习进度详情"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {}

        # 基础统计
        stats = self.get_student_stats(student_id)
        
        # 最近练习历史
        recent_exercises = self.db.query(Exercise).filter(
            Exercise.student_id == student_id,
            Exercise.completed_at.isnot(None)
        ).order_by(Exercise.completed_at.desc()).limit(10).all()

        # 按难度级别的统计
        difficulty_stats = {}
        for exercise in student.exercises:
            if exercise.completed_at:
                diff = exercise.difficulty.value
                if diff not in difficulty_stats:
                    difficulty_stats[diff] = {
                        "count": 0,
                        "total_score": 0,
                        "completed": 0
                    }
                difficulty_stats[diff]["count"] += 1
                if exercise.final_score:
                    difficulty_stats[diff]["total_score"] += exercise.final_score
                    difficulty_stats[diff]["completed"] += 1

        # 计算每个难度的平均分
        for stats in difficulty_stats.values():
            if stats["completed"] > 0:
                stats["average_score"] = round(
                    stats["total_score"] / stats["completed"], 
                    2
                )
            else:
                stats["average_score"] = 0.0

        return {
            **stats,
            "recent_exercises": [
                {
                    "id": ex.id,
                    "date": ex.completed_at.strftime("%Y-%m-%d %H:%M"),
                    "difficulty": ex.difficulty.value,
                    "score": ex.final_score,
                    "time_spent": ex.total_time
                }
                for ex in recent_exercises
            ],
            "difficulty_stats": difficulty_stats
        }