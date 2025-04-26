"""app/schemas/__init__.py
作用：导出所有模型类，方便其他模块导入

通过这个文件，其他模块可以直接从schemas包导入所需的模型，
而不需要关心具体的文件路径，例如：
from app.schemas import UserCreate, ExerciseResponse
"""

from .base import BaseResponse, TimestampMixin, IDMixin
from .user import (
    UserBase, UserCreate, UserUpdate, UserInDB, 
    UserResponse, Token, TokenPayload
)
from .exercise import (
    QuestionBase, QuestionCreate, QuestionUpdate, QuestionResponse,
    ExerciseBase, ExerciseCreate, ExerciseUpdate, ExerciseResponse,
    ExerciseStats, ExerciseListResponse, ExerciseFeedbackRequest
)
from .common import ErrorResponse, PaginationParams, HealthCheck

# __all__变量明确指定了可以从这个模块导入的名称
__all__ = [
    # 基础模型
    "BaseResponse",
    "TimestampMixin",
    "IDMixin",
    
    # 用户相关模型
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "Token",
    "TokenPayload",
    
    # 练习相关模型
    "QuestionBase",
    "QuestionCreate",
    "QuestionUpdate",
    "QuestionResponse",
    "ExerciseBase",
    "ExerciseCreate",
    "ExerciseUpdate",
    "ExerciseResponse",
    "ExerciseStats",
    "ExerciseListResponse",
    "ExerciseFeedbackRequest",
    
    # 通用模型
    "ErrorResponse",
    "PaginationParams",
    "HealthCheck"
]