import random
from .question_factory import QuestionFactory
from ..models.question import Question, OperatorType

class AdditionQuestionFactory(QuestionFactory):
    def create_question(self) -> Question:
        num1, num2 = self._generate_numbers()
        answer = num1 + num2
        content = f"{num1} + {num2} = ?"
        return Question(content, answer, OperatorType.ADDITION)

class SubtractionQuestionFactory(QuestionFactory):
    def create_question(self) -> Question:
        num1, num2 = self._generate_numbers()
        # 确保结果为正数
        num1, num2 = max(num1, num2), min(num1, num2)
        answer = num1 - num2
        content = f"{num1} - {num2} = ?"
        return Question(content, answer, OperatorType.SUBTRACTION)

class MultiplicationQuestionFactory(QuestionFactory):
    def create_question(self) -> Question:
        num1, num2 = self._generate_numbers()
        answer = num1 * num2
        content = f"{num1} × {num2} = ?"
        return Question(content, answer, OperatorType.MULTIPLICATION)

class DivisionQuestionFactory(QuestionFactory):
    def create_question(self) -> Question:
        num2 = random.randint(1, self.max_num)  # 除数不能为0
        answer = random.randint(1, self.max_num)
        num1 = num2 * answer  # 确保能整除
        content = f"{num1} ÷ {num2} = ?"
        return Question(content, float(answer), OperatorType.DIVISION)

class QuestionGenerator:
    def __init__(self, number_range: tuple[int, int]):
        self.factories = {
            OperatorType.ADDITION: AdditionQuestionFactory(number_range),
            OperatorType.SUBTRACTION: SubtractionQuestionFactory(number_range),
            OperatorType.MULTIPLICATION: MultiplicationQuestionFactory(number_range),
            OperatorType.DIVISION: DivisionQuestionFactory(number_range)
        }
    
    def generate_question(self, operator_type: OperatorType) -> Question:
        return self.factories[operator_type].create_question()
