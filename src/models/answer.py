from dataclasses import dataclass
from datetime import datetime
from .question import Question

@dataclass
class Answer:
    question: Question
    submit_time: datetime
    time_spent: int  # 以秒为单位
