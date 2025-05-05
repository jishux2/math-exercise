"""
文件名: app/models/user.py
作用: 定义用户相关的数据模型

数据库关系说明：
1. User <-> Exercise（一对多）：
   - 外键：Exercise.user_id -> User.id
   - 关系属性：
     * User.exercises: 用户创建的所有练习列表
     * Exercise.user: 练习所属的用户
   - 关系行为详见exercise.py中的说明

2. User <-> Student（多对多）：
   - 教师-学生关系：
     * 外键：Student.teacher_id -> User.id
     * 关系属性：
       - User.teacher_students: 教师关联的所有学生
       - Student.teacher: 学生的指导教师
   - 家长-学生关系：
     * 外键：Student.parent_id -> User.id
     * 关系属性：
       - User.students: 家长关联的所有学生
       - Student.parent: 学生的家长
"""

from enum import Enum
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class UserRole(str, Enum):
    """
    用户角色枚举：定义系统中的用户类型
    使用字符串作为枚举值以便于数据库存储和API交互
    """
    STUDENT = "student"    # 学生
    TEACHER = "teacher"    # 教师
    PARENT = "parent"      # 家长
    ADMIN = "admin"        # 管理员

class User(Base):
    """
    用户模型：定义用户的数据结构和属性
    """
    __tablename__ = "users"  # 指定数据库表名

    # 用户的唯一标识符
    id = Column(Integer, primary_key=True, index=True)
    # 用户邮箱，要求唯一且创建索引
    email = Column(String, unique=True, index=True)
    # 用户名，要求唯一且创建索引
    username = Column(String, unique=True, index=True)
    # 密码的哈希值，不存储原始密码
    hashed_password = Column(String)
    # 账户状态标志，默认为激活状态
    is_active = Column(Boolean, default=True)
    # 用户角色，默认为学生角色
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT)
    # 账户创建时间，默认为当前时间
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系字段
    # 用户创建的所有练习列表
    exercises = relationship("Exercise", back_populates="user")
    # 作为家长关联的学生列表
    students = relationship(
        "Student",
        back_populates="parent",
        foreign_keys="Student.parent_id"
    )
    # 作为教师关联的学生列表
    teacher_students = relationship(
        "Student",
        back_populates="teacher",
        foreign_keys="Student.teacher_id"
    )

class Student(Base):
    """
    学生信息模型：存储学生特有的信息和关联关系
    注意：这个模型与User模型是一对一关系，只有角色为学生的用户才会有对应记录
    """
    __tablename__ = "students"  # 指定数据库表名

    # 学生记录的唯一标识符
    id = Column(Integer, primary_key=True, index=True)
    # 关联的用户ID，一对一关系
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    # 关联的教师ID，可以为空
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # 关联的家长ID，可以为空
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # 学生年级
    grade = Column(String)
    # 所在班级
    class_name = Column(String)
    # 记录创建时间
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系字段
    # 关联的用户信息
    user = relationship("User", foreign_keys=[user_id])
    # 关联的教师信息
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_students")
    # 关联的家长信息
    parent = relationship("User", foreign_keys=[parent_id], back_populates="students")