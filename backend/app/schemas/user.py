from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str

    @field_validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError('用户名至少需要3个字符')
        if len(v) > 20:
            raise ValueError('用户名不能超过20个字符')
        return v


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @field_validator('username')
    def username_must_be_valid(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('用户名至少需要3个字符')
            if len(v) > 20:
                raise ValueError('用户名不能超过20个字符')
        return v

    @field_validator('password')
    def password_must_be_strong(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        return v


class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    exercise_count: Optional[int] = None
    average_score: Optional[float] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # 改为str类型
    exp: datetime