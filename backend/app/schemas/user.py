"""app/schemas/user.py
作用：定义用户相关的数据模型

包含：
1. 用户基础、创建、更新、响应等模型
2. 用户认证相关的Token模型
"""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型
    
    包含用户的基本信息字段
    """
    # EmailStr是Pydantic提供的邮箱字段类型，会自动验证邮箱格式
    email: EmailStr
    username: str

    @field_validator('username')
    def username_must_be_valid(cls, v):
        """验证用户名的长度
        
        v: 用户名字符串
        """
        if len(v) < 3:
            raise ValueError('用户名至少需要3个字符')
        if len(v) > 20:
            raise ValueError('用户名不能超过20个字符')
        return v


class UserCreate(UserBase):
    """用户创建模型
    
    继承基础模型，添加密码字段
    """
    password: str

    @field_validator('password')
    def password_must_be_strong(cls, v):
        """验证密码长度
        
        v: 密码字符串
        """
        if len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        return v


class UserUpdate(BaseModel):
    """用户更新模型
    
    所有字段都是可选的，允许部分更新
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @field_validator('username')
    def username_must_be_valid(cls, v):
        """验证用户名长度（如果提供了用户名）
        
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
        
        v: 密码字符串，可能为None
        """
        if v is not None and len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        return v


class UserInDB(UserBase):
    """数据库用户模型
    
    用于内部使用，包含数据库中的额外字段
    """
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """用户响应模型
    
    用于向前端返回用户信息，添加了练习相关的统计字段
    """
    exercise_count: Optional[int] = None    # 练习总数
    average_score: Optional[float] = None   # 平均分数


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
    sub: str       # 主题（通常是用户ID）
    exp: datetime  # 过期时间