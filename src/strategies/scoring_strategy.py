from abc import ABC, abstractmethod
from typing import List
from ..models.answer import Answer

class ScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, answers: List[Answer]) -> float:
        pass
