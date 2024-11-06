from typing import List
from .scoring_strategy import ScoringStrategy
from ..models.answer import Answer

class TimedScoringStrategy(ScoringStrategy):
    def __init__(self, time_weight: float = 0.3, accuracy_weight: float = 0.7):
        self.time_weight = time_weight
        self.accuracy_weight = accuracy_weight
        
    def calculate_score(self, answers: List[Answer]) -> float:
        if not answers:
            return 0.0
        
        # 计算正确率分数
        correct_count = sum(1 for answer in answers 
                          if answer.question.check_answer())
        accuracy_score = correct_count / len(answers) * 100
        
        # 计算时间分数
        avg_time = sum(answer.time_spent for answer in answers) / len(answers)
        time_score = max(0, 100 - (avg_time - 30) * 2)  # 30秒为基准时间
        
        # 计算总分
        final_score = (accuracy_score * self.accuracy_weight + 
                      time_score * self.time_weight)
        return round(final_score, 2)

class AccuracyScoringStrategy(ScoringStrategy):
    def calculate_score(self, answers: List[Answer]) -> float:
        if not answers:
            return 0.0
        
        correct_count = sum(1 for answer in answers 
                          if answer.question.check_answer())
        return round(correct_count / len(answers) * 100, 2)