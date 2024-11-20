# src/factories/question_factory.py

from abc import ABC, abstractmethod
from collections import deque
import random
from typing import List, Tuple, Optional
from ..models.question import Question, OperatorType, DifficultyLevel
from ..models.arithmetic_tree import ArithmeticTree, ArithmeticNode


class QuestionFactory(ABC):
    def __init__(
        self,
        difficulty: DifficultyLevel,
        number_range: tuple[int, int],
        operators: List[OperatorType],
    ):
        self.difficulty = difficulty
        self.min_num = number_range[0]
        self.max_num = number_range[1]
        self.operators = operators
        self.tree = ArithmeticTree()

    @abstractmethod
    def create_question(self) -> Question:
        pass

    def _get_operand_count(self) -> int:
        """根据难度确定操作数个数"""
        if self.difficulty == DifficultyLevel.EASY:
            return 2
        elif self.difficulty == DifficultyLevel.MEDIUM:
            return 3
        else:
            return 4

    def _generate_node(self) -> ArithmeticNode:
        """生成初始节点"""
        return ArithmeticNode(
            operand=random.randint(self.min_num, self.max_num),
            operator=self._get_random_operator(),
        )

    def _get_random_operator(self) -> OperatorType:
        """随机选择运算符"""
        return random.choice(self.operators)

    def _get_weighted_result(self, operator: OperatorType) -> int:
        """根据运算符类型获取加权随机的结果"""
        from math import floor, ceil

        if operator != OperatorType.DIVISION:
            return random.randint(self.min_num, self.max_num)

        a, b = self.min_num, self.max_num
        result_weights = []  # [(result, weight)]

        # 跳过0、1、-1这些特殊值
        skip_values = {0, 1, -1}

        if b > a > 0:  # 正数范围
            for n in range(a, floor(b / 2) + 1):
                if n in skip_values:
                    continue
                count = floor(b / n) - 1  # 减1是因为不考虑x/1=x的情况
                if count > 0:
                    result_weights.append((n, count))

        elif a < b < 0:  # 负数范围
            for n in range(ceil(a / 2), b + 1):
                if n in skip_values:
                    continue
                count = floor(a / n) - 1
                if count > 0:
                    result_weights.append((n, count))

        elif a <= 0 <= b:  # 跨越0的范围
            # 确定考虑范围的边界
            upper_limit = max(-a, b) / 2
            lower_limit = min(a, -b) / 2

            upper_limit = min(b, floor(upper_limit))
            lower_limit = max(a, ceil(lower_limit))

            for n in range(lower_limit, upper_limit + 1):
                if n in skip_values:
                    continue
                count = 0
                if a < 0:
                    count += floor(abs(a / n)) - 1
                if b > 0:
                    count += floor(abs(b / n)) - 1
                if count > 0:
                    result_weights.append((n, count))

        if not result_weights:  # 如果没有找到合适的结果
            return random.randint(self.min_num, self.max_num)  # 退化为普通随机

        # 根据权重随机选择结果
        total_weight = sum(weight for _, weight in result_weights)
        r = random.uniform(0, total_weight)
        current_weight = 0
        for result, weight in result_weights:
            current_weight += weight
            if r <= current_weight:
                return result

        return result_weights[-1][0]  # 保险起见返回最后一个可能的结果

    def _generate_operands(
        self, operator: OperatorType, result: int
    ) -> Tuple[Optional[int], Optional[int]]:
        """根据运算符和结果生成合适的操作数"""
        from math import floor, ceil

        min_num, max_num = self.min_num, self.max_num

        if operator == OperatorType.ADDITION:
            # 计算left可能的取值范围
            left_min = max(result - max_num, min_num)
            left_max = min(result - min_num, max_num)
            
            # 检查是否是空集
            if left_min > left_max:
                return None, None
                
            left = random.randint(left_min, left_max)
            right = result - left
            return left, right
            
        elif operator == OperatorType.SUBTRACTION:
            # 计算left可能的取值范围
            left_min = max(min_num, result + min_num)
            left_max = min(max_num, result + max_num)
            
            # 检查是否是空集
            if left_min > left_max:
                return None, None
                
            left = random.randint(left_min, left_max)
            right = left - result
            return left, right

        elif operator == OperatorType.MULTIPLICATION:
            if result == 0:
                return random.randint(min_num, max_num), 0
            factors = []
            for i in range(min_num, min(result + 1, max_num + 1)):
                if i == 0:
                    continue
                if result % i == 0 and min_num <= result // i <= max_num:
                    factors.append(i)
            if not factors:
                return None, None
            left = random.choice(factors)
            return left, result // left

        else:  # DIVISION
            if result == 0 or abs(result) == 1:
                return None, None

            possible_dividers = []

            # 根据[min_num, max_num]的范围情况来确定除数范围
            if max_num > min_num > 0:  # 全正数范围
                upper_limit = floor(max_num / result)
                if upper_limit >= 2:
                    possible_dividers.extend(range(2, upper_limit + 1))

            elif min_num < max_num < 0:  # 全负数范围
                lower_limit = ceil(min_num / result)
                if lower_limit <= -2:
                    possible_dividers.extend(range(lower_limit, -1))

            elif min_num <= 0 <= max_num:  # 跨越0的范围
                # 对于正除数
                if max_num > 0:
                    upper_limit = floor(max_num / abs(result))
                    if upper_limit >= 2:
                        possible_dividers.extend(range(2, upper_limit + 1))

                # 对于负除数
                if min_num < 0:
                    lower_limit = ceil(-abs(min_num / result))
                    if lower_limit <= -2:
                        possible_dividers.extend(range(lower_limit, -1))

            if not possible_dividers:
                return None, None

            # 随机选择一个除数
            right = random.choice(possible_dividers)
            left = result * right

            # 验证生成的被除数是否在允许范围内
            if min_num <= left <= max_num:
                return left, right

            return None, None
