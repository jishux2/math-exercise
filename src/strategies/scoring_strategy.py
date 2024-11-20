from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.answer import Answer
from ..models.question import DifficultyLevel


class ScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(
        self, answers: List[Answer], difficulty: Optional[DifficultyLevel] = None
    ) -> float:
        pass
