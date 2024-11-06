from dataclasses import dataclass
from enum import Enum
from typing import Optional

class OperatorType(Enum):
    ADDITION = '+'
    SUBTRACTION = '-'
    MULTIPLICATION = '*'
    DIVISION = '/'

@dataclass
class Question:
    content: str
    answer: float
    operator_type: OperatorType
    user_answer: Optional[float] = None
    
    def check_answer(self) -> bool:
        return abs(self.answer - self.user_answer) < 0.001
