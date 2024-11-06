from typing import List
import random
from datetime import datetime
from ..models.question import Question, OperatorType
from ..models.answer import Answer
from ..factories.concrete_factories import QuestionGenerator
from ..observers.exercise_observer import ExerciseObserver, ExerciseStatus
from ..strategies.scoring_strategy import ScoringStrategy
from ..strategies.concrete_strategies import AccuracyScoringStrategy

class Exercise:
    def __init__(self, difficulty_level: str, number_range: tuple[int, int]):
        self.status = ExerciseStatus.NOT_STARTED
        self.questions: List[Question] = []
        self.answers: List[Answer] = []
        self.observers: List[ExerciseObserver] = []
        self.scoring_strategy: ScoringStrategy = AccuracyScoringStrategy()
        self.question_generator = QuestionGenerator(number_range)
    
    def add_observer(self, observer: ExerciseObserver):
        self.observers.append(observer)
    
    def remove_observer(self, observer: ExerciseObserver):
        self.observers.remove(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            observer.on_exercise_state_changed(self.status)
    
    def set_scoring_strategy(self, strategy: ScoringStrategy):
        self.scoring_strategy = strategy
    
    def generate_questions(self, operator_types: List[OperatorType], count: int):
        self.status = ExerciseStatus.IN_PROGRESS
        self.notify_observers()
        
        for _ in range(count):
            operator_type = random.choice(operator_types)
            question = self.question_generator.generate_question(operator_type)
            self.questions.append(question)
    
    def submit_answer(self, question_index: int, user_answer: float, time_spent: int):
        if question_index >= len(self.questions):
            raise ValueError("题目索引越界")
        
        question = self.questions[question_index]
        question.user_answer = user_answer
        
        answer = Answer(
            question=question,
            submit_time=datetime.now(),
            time_spent=time_spent
        )
        self.answers.append(answer)
    
    def submit_exercise(self):
        if len(self.answers) != len(self.questions):
            raise ValueError("还有题目未完成")
        
        self.status = ExerciseStatus.SUBMITTED
        self.notify_observers()
        
        final_score = self.scoring_strategy.calculate_score(self.answers)
        
        self.status = ExerciseStatus.GRADED
        self.notify_observers()
        
        return final_score