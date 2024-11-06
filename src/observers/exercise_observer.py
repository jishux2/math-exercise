from abc import ABC, abstractmethod
from enum import Enum

class ExerciseStatus(Enum):
    NOT_STARTED = "未开始"
    IN_PROGRESS = "进行中"
    SUBMITTED = "已提交"
    GRADED = "已批改"

class ExerciseObserver(ABC):
    @abstractmethod
    def on_exercise_state_changed(self, status: ExerciseStatus):
        pass
