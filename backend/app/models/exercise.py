from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case, cast, Float, func
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, 
    Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"

class OperatorType(str, Enum):
    ADDITION = "+"
    SUBTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    difficulty = Column(SQLEnum(DifficultyLevel))
    number_range = Column(JSON)  # 存储为JSON: [min, max]
    operator_types = Column(JSON)  # 存储为JSON数组
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    final_score = Column(Float, nullable=True)
    total_time = Column(Integer, nullable=True)
    ai_feedback = Column(String, nullable=True)

    questions = relationship("Question", back_populates="exercise")
    user = relationship("User", back_populates="exercises")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    content = Column(String)
    correct_answer = Column(Float)
    user_answer = Column(Float, nullable=True)
    time_spent = Column(Integer, nullable=True)
    operator_types = Column(JSON)  # 存储为JSON数组
    arithmetic_tree = Column(JSON, nullable=True)  # 存储题目的算术树结构

    exercise = relationship("Exercise", back_populates="questions")
    
    @hybrid_property
    def is_correct(self) -> bool:
        if self.user_answer is None:
            return False
        return abs(self.correct_answer - self.user_answer) < 0.001

    @is_correct.expression
    def is_correct(cls):
        # 在数据库层面实现计算
        return case(
            (cls.user_answer.is_(None), False),
            else_=func.abs(
                cls.correct_answer - cast(cls.user_answer, Float)
            ) < 0.001
        )

    def to_response(self) -> "QuestionResponse":
        """转换为响应对象的辅助方法"""
        from ..schemas.exercise import QuestionResponse  # 避免循环导入
        return QuestionResponse(
            id=self.id,
            exercise_id=self.exercise_id,
            content=self.content,
            operator_types=self.operator_types,
            arithmetic_tree=self.arithmetic_tree,
            correct_answer=self.correct_answer,
            user_answer=self.user_answer,
            time_spent=self.time_spent,
            is_correct=self.is_correct
        )