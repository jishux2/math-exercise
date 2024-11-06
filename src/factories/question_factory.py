from abc import ABC, abstractmethod
import random
from ..models.question import Question, OperatorType

class QuestionFactory(ABC):
    def __init__(self, number_range: tuple[int, int]):
        self.min_num = number_range[0]
        self.max_num = number_range[1]
    
    @abstractmethod
    def create_question(self) -> Question:
        pass
    
    def _generate_numbers(self) -> tuple[int, int]:
        return (random.randint(self.min_num, self.max_num),
                random.randint(self.min_num, self.max_num))
