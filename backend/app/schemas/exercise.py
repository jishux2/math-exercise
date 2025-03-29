from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Tuple
from datetime import datetime
from ..models.exercise import DifficultyLevel, OperatorType


class QuestionBase(BaseModel):
    content: str
    operator_types: List[OperatorType]
    arithmetic_tree: Optional[dict] = None


class QuestionCreate(QuestionBase):
    correct_answer: float


class QuestionUpdate(BaseModel):
    user_answer: float
    time_spent: int = Field(..., gt=0, description="答题用时（秒）")


class QuestionResponse(QuestionBase):
    id: int
    exercise_id: int
    correct_answer: float  # 添加这个字段
    user_answer: Optional[float] = None
    time_spent: Optional[int] = None
    is_correct: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ExerciseBase(BaseModel):
    difficulty: DifficultyLevel
    number_range: Tuple[int, int] = Field(..., description="数值范围 [最小值, 最大值]")
    operator_types: List[OperatorType]

    @field_validator('number_range')
    def validate_number_range(cls, v):
        if len(v) != 2:
            raise ValueError('数值范围必须包含两个值 [min, max]')
        if v[0] >= v[1]:
            raise ValueError('最小值必须小于最大值')
        return v

    @field_validator('operator_types')
    def validate_operator_types(cls, v):
        if not v:
            raise ValueError('至少需要选择一种运算符')
        return v


class ExerciseCreate(ExerciseBase):
    question_count: int = Field(..., gt=0, le=100, description="题目数量")


class ExerciseUpdate(BaseModel):
    ai_feedback: Optional[str] = None


class ExerciseResponse(ExerciseBase):
    id: int
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    final_score: Optional[float] = None
    total_time: Optional[int] = None
    ai_feedback: Optional[str] = None
    questions: List[QuestionResponse]

    model_config = ConfigDict(from_attributes=True)


class ExerciseStats(BaseModel):
    total_exercises: int
    completed_exercises: int
    average_score: float
    total_time: int
    accuracy_rate: float
    favorite_operator: OperatorType
    best_difficulty: DifficultyLevel


class ExerciseListResponse(BaseModel):
    exercises: List[ExerciseResponse]
    total: int
    page: int
    page_size: int


class ExerciseFeedbackRequest(BaseModel):
    exercise_id: int
    feedback_type: str = Field(..., description="反馈类型：'detailed' 或 'summary'")