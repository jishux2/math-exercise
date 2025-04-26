"""
文件名: app/models/user.py
作用: 定义用户相关的数据模型

数据库关系说明：
User <-> Exercise（一对多）：
- 外键：Exercise.user_id -> User.id
- 关系属性：
  * User.exercises: 用户创建的所有练习列表
  * Exercise.user: 练习所属的用户
- 关系行为详见exercise.py中的说明
"""

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

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
    # 账户创建时间，默认为当前时间
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 用户创建的所有练习列表，对应Exercise模型中的user属性
    exercises = relationship("Exercise", back_populates="user")