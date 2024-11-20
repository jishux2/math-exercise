import random
from typing import List
from collections import deque
from ..models.question import Question, OperatorType, DifficultyLevel
from .question_factory import QuestionFactory
from ..models.arithmetic_tree import ArithmeticNode


class ArithmeticQuestionFactory(QuestionFactory):
    def create_question(self) -> Question:
        operand_count = self._get_operand_count()
        incomplete_nodes = []  # 存储所有未完成的节点

        # 初始节点的结果使用加权随机
        initial_operator = self._get_random_operator()
        initial_result = self._get_suitable_result(initial_operator)

        root_node = ArithmeticNode(operand=initial_result, operator=initial_operator)
        self.tree.root = root_node
        incomplete_nodes.append(root_node)

        count = 1
        operators = []  # 记录使用的运算符
        check = False

        while count < operand_count:
            # 随机选择一个未完成的节点
            current_node = random.choice(incomplete_nodes)
            incomplete_nodes.remove(current_node)  # 从列表中移除选中的节点
            operator = current_node.operator
            operand = current_node.operand

            left_node = ArithmeticNode(0)
            right_node = ArithmeticNode(0)
            left_node.operator = (
                self._get_random_operator() if count < operand_count - 1 else None
            )
            right_node.operator = (
                self._get_random_operator() if count < operand_count - 1 else None
            )

            left_num, right_num = None, None
            retry_count = 0
            max_retries = 10  # 最大重试次数

            while (left_num is None or right_num is None) and retry_count < max_retries:
                left_num, right_num = self._generate_operands(operator, operand)
                if left_num is None or right_num is None:
                    # 如果生成失败，重新选择运算符
                    current_node.operator = self._get_random_operator()
                    operator = current_node.operator
                retry_count += 1

            if retry_count >= max_retries:
                raise ValueError("无法生成合适的操作数")

            operators.append(operator)  # 记录运算符

            left_node.operand = left_num
            right_node.operand = right_num
            current_node.set_left_node(left_node)
            current_node.set_right_node(right_node)

            # 如果还需要继续生成节点，将新生成的有运算符的节点加入待处理列表
            if count < operand_count - 1:
                if left_node.operator is not None:
                    incomplete_nodes.append(left_node)
                if right_node.operator is not None:
                    incomplete_nodes.append(right_node)

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
