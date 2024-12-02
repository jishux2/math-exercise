"""
具体题目工厂模块

本模块实现具体的题目生成工厂类，主要功能：
1. 继承QuestionFactory抽象类，实现实际的题目生成逻辑
2. 实现算术表达式树的构建
3. 生成随机且合理的算术题目

核心类：
- ArithmeticQuestionFactory：算术题目工厂，负责生成具体的算术题目
- QuestionGenerator：工厂类的包装器，提供更简单的接口来生成题目
"""

# 导入所需的库
import random
from typing import List
from collections import deque
from ..models.question import Question, OperatorType, DifficultyLevel
from .question_factory import QuestionFactory
from ..models.arithmetic_tree import ArithmeticNode


class ArithmeticQuestionFactory(QuestionFactory):
    def create_question(self) -> Question:
        """创建一个新的算术题
        根据工厂的配置（难度、数值范围、运算符）生成一个完整的算术表达式题目
        """
        # 获取根据难度确定的操作数个数
        operand_count = self._get_operand_count()
        # 用于存储所有未完成（需要继续处理）的节点
        incomplete_nodes = []

        # 随机选择初始运算符和生成合适的结果值
        initial_operator = self._get_random_operator()
        initial_result = self._get_suitable_result(initial_operator)

        # 创建算术树的根节点，使用初始结果值和运算符
        root_node = ArithmeticNode(operand=initial_result, operator=initial_operator)
        self.tree.root = root_node
        incomplete_nodes.append(root_node)

        count = 1  # 当前已处理的操作数计数
        operators = []  # 记录使用的运算符列表
        check = False  # 用于Debug的标志（当前未使用）

        # 继续生成节点，直到达到所需的操作数个数
        while count < operand_count:
            # 从未完成节点列表中随机选择一个节点进行处理
            current_node = random.choice(incomplete_nodes)
            incomplete_nodes.remove(current_node)  # 移除已选择的节点
            operator = current_node.operator
            operand = current_node.operand

            # 为当前节点创建左右子节点
            left_node = ArithmeticNode(0)
            right_node = ArithmeticNode(0)
            # 如果还需要继续添加操作数，则为新节点分配运算符
            left_node.operator = (
                self._get_random_operator() if count < operand_count - 1 else None
            )
            right_node.operator = (
                self._get_random_operator() if count < operand_count - 1 else None
            )

            # 初始化左右操作数为None
            left_num, right_num = None, None
            retry_count = 0  # 重试计数器
            max_retries = 10  # 最大重试次数

            # 尝试生成合适的操作数
            while (left_num is None or right_num is None) and retry_count < max_retries:
                left_num, right_num = self._generate_operands(operator, operand)
                if left_num is None or right_num is None:
                    # 如果生成失败，重新选择运算符再试
                    current_node.operator = self._get_random_operator()
                    operator = current_node.operator
                retry_count += 1

            # 如果达到最大重试次数仍然失败，抛出异常
            if retry_count >= max_retries:
                raise ValueError("无法生成合适的操作数")

            operators.append(operator)  # 记录使用的运算符

            # 设置左右子节点的值
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

            count += 1  # 更新操作数计数

        # 生成算术表达式字符串
        arithmetic = self.tree.get_arithmetic()
        # 计算表达式结果
        result = self._calculate_result(arithmetic)
        # 创建并返回Question对象
        return Question(content=arithmetic, answer=result, operator_types=operators)

    def _calculate_result(self, expression: str) -> float:
        """计算表达式的结果
        注：实际应用中应该实现一个安全的表达式计算器

        Args:
            expression (str): 要计算的表达式字符串

        Returns:
            float: 表达式的计算结果
        """
        # 将除号替换为Python的除法运算符，然后使用eval计算
        # 注意：这种方法不安全，实际应用中应该使用更安全的实现
        return eval(expression.replace("÷", "/"))


class QuestionGenerator:
    """问题生成器类，封装了工厂的创建和使用"""

    def __init__(
        self,
        difficulty: DifficultyLevel,
        number_range: tuple[int, int],
        operators: List[OperatorType],
    ):
        """初始化问题生成器

        Args:
            difficulty: 难度级别
            number_range: 数值范围的元组(最小值, 最大值)
            operators: 允许使用的运算符列表
        """
        # 创建具体的算术题工厂实例
        self.factory = ArithmeticQuestionFactory(difficulty, number_range, operators)

    def generate_question(self) -> Question:
        """生成一个新的问题

        Returns:
            Question: 生成的问题对象
        """
        # 通过工厂创建并返回一个新的问题
        return self.factory.create_question()
