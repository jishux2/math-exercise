from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class DifficultyLevel(Enum):
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"


class OperatorType(Enum):
    ADDITION = "+"
    SUBTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"


@dataclass
class Question:
    content: str
    answer: float
    operator_types: List[OperatorType]  # 改为列表，因为可能有多个运算符
    user_answer: Optional[float] = None

    def check_answer(self) -> bool:
        return abs(self.answer - self.user_answer) < 0.001
