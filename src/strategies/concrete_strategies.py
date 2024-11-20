from typing import List, Optional
from .scoring_strategy import ScoringStrategy
from ..models.answer import Answer
from ..models.question import DifficultyLevel


class TimedScoringStrategy(ScoringStrategy):
    def __init__(self, time_weight: float = 0.3, accuracy_weight: float = 0.7):
        if not (0 < time_weight < 1 and 0 < accuracy_weight < 1):
            raise ValueError("权重必须在0到1之间")
        if abs(time_weight + accuracy_weight - 1) > 0.0001:  # 使用epsilon比较浮点数
            raise ValueError("权重之和必须等于1")

        self.time_weight = time_weight
        self.accuracy_weight = accuracy_weight

    def calculate_score(
        self, answers: List[Answer], difficulty: Optional[DifficultyLevel] = None
    ) -> float:
        if not answers:
            return 0.0

        if difficulty is None:
            raise ValueError("TimedScoringStrategy需要difficulty参数")

        # 计算正确率分数
        correct_count = sum(1 for answer in answers if answer.is_correct)
        accuracy_score = correct_count / len(answers) * 100

        # 根据难度和题目数量计算基准时间（秒）
        base_times = {
            DifficultyLevel.EASY: 30,  # 简单题平均30秒
            DifficultyLevel.MEDIUM: 45,  # 中等题平均45秒
            DifficultyLevel.HARD: 60,  # 困难题平均60秒
        }

        base_time_per_question = base_times[difficulty]
        total_base_time = base_time_per_question * len(answers)

        # 计算实际用时
        total_time = sum(answer.time_spent for answer in answers)

        # 计算时间分数
        if total_time <= total_base_time:
            time_score = 100
        else:
            overtime_ratio = (total_time - total_base_time) / total_base_time
            time_score = max(0, min(100, 100 - overtime_ratio * 100))

        # 计算总分
        final_score = (
            accuracy_score * self.accuracy_weight + time_score * self.time_weight
        )

        return round(final_score, 2)


class AccuracyScoringStrategy(ScoringStrategy):
    def calculate_score(
        self, answers: List[Answer], difficulty: Optional[DifficultyLevel] = None
    ) -> float:
        if not answers:
            return 0.0

        correct_count = sum(1 for answer in answers if answer.is_correct)
        return round(correct_count / len(answers) * 100, 2)
