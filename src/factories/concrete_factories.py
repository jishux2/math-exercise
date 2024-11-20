from typing import List
from collections import deque
from ..models.question import Question, OperatorType, DifficultyLevel
from .question_factory import QuestionFactory
from ..models.arithmetic_tree import ArithmeticNode


class ArithmeticQuestionFactory(QuestionFactory):
    def create_question(self) -> Question:
        operand_count = self._get_operand_count()

        # 初始节点的结果使用加权随机
        initial_operator = self._get_random_operator()
        initial_result = self._get_suitable_result(initial_operator)

        self.tree.root = ArithmeticNode(
            operand=initial_result, operator=initial_operator
        )

        count = 1
        queue = deque([self.tree.root])
        operators = []  # 记录使用的运算符
        check=False

        while count < operand_count:
            current_node = queue[0]
            operator = current_node.operator
            operand = current_node.operand

            left_node = ArithmeticNode(0)
            right_node = ArithmeticNode(0)
            left_node.operator = self._get_random_operator()
            right_node.operator = self._get_random_operator()

            # 根据不同运算符生成合适的操作数
            left_num, right_num = self._generate_operands(operator, operand)
            if not check:
                check=True

            if left_num is None or right_num is None:
                # 如果生成失败，重新选择运算符
                current_node.operator = self._get_random_operator()
                continue

            queue.popleft()
            operators.append(operator)  # 记录运算符

            left_node.operand = left_num
            right_node.operand = right_num
            current_node.set_left_node(left_node)
            current_node.set_right_node(right_node)

            queue.extend([left_node, right_node])
            count += 1

        arithmetic = self.tree.get_arithmetic()
        # 使用更安全的方式计算结果
        result = self._calculate_result(arithmetic)
        return Question(content=arithmetic, answer=result, operator_types=operators)

    def _calculate_result(self, expression: str) -> float:
        """安全地计算表达式结果"""
        # 这里应该实现一个安全的表达式求值器
        # 暂时使用eval，实际应用中应该替换为更安全的实现
        return eval(expression.replace("÷", "/"))


class QuestionGenerator:
    def __init__(
        self,
        difficulty: DifficultyLevel,
        number_range: tuple[int, int],
        operators: List[OperatorType],
    ):
        self.factory = ArithmeticQuestionFactory(difficulty, number_range, operators)

    def generate_question(self) -> Question:
        return self.factory.create_question()
