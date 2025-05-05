"""app/schemas/user.py
作用：定义用户相关的数据模型

包含：
1. 用户基础、创建、更新、响应等模型
2. 不同角色用户（学生、教师、家长、管理员）的专用模型
3. 用户认证相关的Token模型
"""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from ..models.user import UserRole


class UserBase(BaseModel):
    """用户基础模型
    
    包含用户的基本信息字段，所有用户类型共用的属性
    """
    email: EmailStr                               # EmailStr是Pydantic提供的邮箱字段类型，会自动验证邮箱格式
    username: str                                 # 用户名
    role: Optional[UserRole] = UserRole.STUDENT   # 用户角色，默认为学生

    @field_validator('username')
    def username_must_be_valid(cls, v):
        """验证用户名的长度
        
        Args:
            v: 用户名字符串
        """
        if len(v) < 3:
            raise ValueError('用户名至少需要3个字符')
        if len(v) > 20:
            raise ValueError('用户名不能超过20个字符')
        return v

class StudentInfo(BaseModel):
    """学生特有信息模型
    
    包含只有学生角色才需要的额外信息
    """
    grade: str        # 年级
    class_name: str   # 班级

class UserCreate(UserBase):
    """用户创建模型
    
    继承基础模型，添加密码字段和学生信息字段
    """
    password: str                                 # 密码
    student_info: Optional[StudentInfo] = None    # 学生特有信息，仅当role为STUDENT时使用

    @field_validator('password')
    def password_must_be_strong(cls, v):
        """验证密码长度
        
        Args:
            v: 密码字符串
        """
        if len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        return v

class TeacherCreate(UserCreate):
    """教师用户创建模型
    
    继承用户创建模型，添加教师特有字段
    """
    role: UserRole = UserRole.TEACHER  # 固定角色为教师
    subjects: List[str]                # 教授科目列表

class ParentCreate(UserCreate):
    """家长用户创建模型
    
    继承用户创建模型，添加家长特有字段
    """
    role: UserRole = UserRole.PARENT   # 固定角色为家长
    student_emails: List[str]          # 关联的学生邮箱列表

class AdminCreate(UserCreate):
    """管理员用户创建模型
    
    继承用户创建模型，固定角色为管理员
    """
    role: UserRole = UserRole.ADMIN    # 固定角色为管理员

class UserUpdate(BaseModel):
    """用户更新模型
    
    所有字段都是可选的，允许部分更新
    """
    email: Optional[EmailStr] = None           # 可选的邮箱更新
    username: Optional[str] = None             # 可选的用户名更新
    password: Optional[str] = None             # 可选的密码更新
    student_info: Optional[StudentInfo] = None # 可选的学生信息更新

    @field_validator('username')
    def username_must_be_valid(cls, v):
        """验证用户名长度（如果提供了用户名）
        
        Args:
            v: 用户名字符串，可能为None
        """
        if v is not None:
            if len(v) < 3:
                raise ValueError('用户名至少需要3个字符')
            if len(v) > 20:
                raise ValueError('用户名不能超过20个字符')
        return v

    @field_validator('password')
    def password_must_be_strong(cls, v):
        """验证密码长度（如果提供了密码）
        
        Args:
            v: 密码字符串，可能为None
        """
        if v is not None and len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        return v

class UserInDB(UserBase):
    """数据库用户模型
    
    用于内部使用，包含数据库中的额外字段
    """
    id: int              # 用户ID
    is_active: bool      # 账户是否激活
    role: UserRole       # 用户角色
    created_at: datetime # 创建时间

    model_config = ConfigDict(from_attributes=True)

class StudentResponse(BaseModel):
    """学生信息响应模型
    
    用于向前端返回学生特有的信息
    """
    id: int                               # 学生ID
    grade: str                           # 年级
    class_name: str                      # 班级
    teacher_name: Optional[str] = None   # 教师姓名（如果有）
    parent_name: Optional[str] = None    # 家长姓名（如果有）

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserInDB):
    """用户响应模型
    
    用于向前端返回用户信息，包含统计信息和额外字段
    """
    exercise_count: Optional[int] = None        # 练习总数
    average_score: Optional[float] = None       # 平均分数
    student_info: Optional[StudentResponse] = None  # 学生信息（仅当用户是学生时）

class Token(BaseModel):
    """JWT令牌模型
    
    用于用户认证的令牌响应
    """
    access_token: str           # 访问令牌
    token_type: str = "bearer"  # 令牌类型，固定为"bearer"

class TokenPayload(BaseModel):
    """令牌载荷模型
    
    定义JWT令牌中包含的数据
    """
    sub: str       # 主题（用户ID）
    exp: datetime  # 过期时间