"""app/schemas/base.py
作用：定义基础的Pydantic模型

这个文件定义了一些基础的数据模型类，它们会被其他模型继承，用于：
1. 提供通用的响应格式
2. 提供时间戳字段
3. 提供ID字段
"""

from pydantic import BaseModel
# BaseModel：Pydantic的基础模型类
# 所有Pydantic模型都要继承这个类
# 它提供了数据验证、序列化等功能

from datetime import datetime
# datetime：日期时间类型
# 用于处理时间戳字段

from typing import Optional
# Optional：类型提示，表示该字段可以是None
# 例如：Optional[str]表示字段可以是字符串或None


class BaseResponse(BaseModel):
    """基础响应模型
    
    所有API响应的基础格式，包含：
    - success: 表示操作是否成功
    - message: 响应信息
    
    示例：
    {
        "success": true,
        "message": "User created successfully"
    }
    """
    success: bool = True    # 操作是否成功，默认为True
    message: str = "Success"  # 响应信息，默认为"Success"


class TimestampMixin(BaseModel):
    """时间戳混入类
    
    为模型添加创建时间和更新时间字段
    
    这是一个Mixin类，用于：
    1. 追踪记录的创建和修改时间
    2. 可以被其他模型通过多重继承方式使用
    
    示例：
    class User(TimestampMixin, BaseModel):
        username: str
    """
    created_at: datetime           # 创建时间，必填字段
    updated_at: Optional[datetime] = None  # 更新时间，可选字段
    # 定义为Optional是因为：
    # 1. 新创建的记录还没有更新时间
    # 2. 不是所有模型都需要跟踪更新时间


class IDMixin(BaseModel):
    """ID混入类
    
    为模型添加ID字段
    
    这是一个Mixin类，用于：
    1. 提供通用的ID字段
    2. 可以被其他需要ID字段的模型继承
    
    示例：
    class UserResponse(IDMixin, BaseModel):
        username: str
    
    会生成如下格式的数据：
    {
        "id": 1,
        "username": "john"
    }
    """
    id: int  # 记录的唯一标识符
    # 通常是数据库的自增主键
    # 定义为int类型，确保ID始终是整数