from abc import ABC, abstractmethod
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
        # 存储范围内的合数
        self.composite_numbers = self._get_composite_numbers()
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

    def _get_suitable_result(self, operator: OperatorType) -> Optional[int]:
        """根据运算符类型获取合适的结果值"""
        from math import floor, ceil

        min_num, max_num = self.min_num, self.max_num

        if operator in (OperatorType.ADDITION, OperatorType.SUBTRACTION):
            return random.randint(min_num, max_num)

        elif operator == OperatorType.MULTIPLICATION:
            if not self.composite_numbers:
                return None
            return random.choice(list(self.composite_numbers))

        elif operator == OperatorType.DIVISION:
            if min_num >= 0:  # 全正数范围
                # 跳过0、1这些特殊值
                skip_values = {0, 1}
                candidates = []

                # 对于每个可能的商
                for n in range(max(2, min_num), floor(max_num / 2) + 1):
                    # 计算有多少个数能被n整除且商在范围内
                    count = sum(
                        1
                        for i in range(2, floor(max_num / n) + 1)
                        if min_num <= n * i <= max_num and i not in skip_values
                    )
                    if count > 0:
                        candidates.extend([n] * count)

            elif max_num <= 0:  # 全负数范围
                # 跳过0、-1这些特殊值
                skip_values = {0, -1}
                candidates = []

                # 对于每个可能的商
                for n in range(ceil(min_num / 2), min(-2, max_num + 1)):
                    # 计算有多少个数能被n整除且商在范围内
                    count = sum(
                        1
                        for i in range(ceil(min_num / n), -1)
                        if min_num <= n * i <= max_num and i not in skip_values
                    )
                    if count > 0:
                        candidates.extend([n] * count)

            else:  # 跨越0的范围
                max_abs = max(abs(min_num), abs(max_num))
                skip_values = {-1, 0, 1}
                candidates = []

                # 正商
                if max_num > 0:
                    for n in range(2, floor(max_num / 2) + 1):
                        count = sum(
                            1
                            for i in range(2, floor(max_num / n) + 1)
                            if min_num <= n * i <= max_num and i not in skip_values
                        )
                        if count > 0:
                            candidates.extend([n] * count)

                # 负商
                if min_num < 0:
                    for n in range(ceil(min_num / 2), -2):
                        count = sum(
                            1
                            for i in range(ceil(min_num / n), -2)
                            if min_num <= n * i <= max_num and i not in skip_values
                        )
                        if count > 0:
                            candidates.extend([n] * count)

            if not candidates:
                return None

            return random.choice(candidates)

        return None  # 对于未知的运算符返回None

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
                
            # 在[-abs(result)+1, abs(result)-1]范围内寻找因数，排除±1
            factors = []
            search_start = max(-abs(result) + 1, min_num)
            search_end = min(abs(result) - 1, max_num)
            
            for i in range(search_start, search_end + 1):
                if i in {-1, 0, 1}:  # 排除0和±1
                    continue
                if (result % i == 0 and 
                    min_num <= result // i <= max_num):  # 确保另一个因数也在范围内
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

    def _sieve_of_eratosthenes(self, n: int) -> set[int]:
        """埃拉托斯特尼筛法，找出n以内的所有素数"""
        # 初始化标记数组，默认所有数都是素数
        is_prime = [True] * (n + 1)
        is_prime[0] = is_prime[1] = False

        # 从2开始遍历到sqrt(n)
        for i in range(2, int(n**0.5) + 1):
            if is_prime[i]:
                # 将i的所有倍数标记为非素数
                for j in range(i * i, n + 1, i):
                    is_prime[j] = False

        # 返回所有素数
        return {i for i in range(2, n + 1) if is_prime[i]}

    def _get_composite_numbers(self) -> set[int]:
        """获取数值范围内的所有合数"""
        min_num, max_num = self.min_num, self.max_num

        if min_num >= 0:  # 全正数范围
            primes = self._sieve_of_eratosthenes(max_num)
            # 排除1和素数
            return set(range(min_num, max_num + 1)) - primes - {0, 1}

        elif max_num <= 0:  # 全负数范围
            primes = self._sieve_of_eratosthenes(-min_num)
            # 取相反数，排除-1
            return {
                -x for x in range(-max_num, -min_num + 1) if x not in primes and x != 1
            }

        else:  # 跨越0的范围
            max_abs = max(abs(min_num), abs(max_num))
            primes = self._sieve_of_eratosthenes(max_abs)
            result = set()

            # 添加正数范围
            if max_num > 0:
                result.update(
                    set(range(1 if min_num <= 0 else min_num, max_num + 1))
                    - primes
                    - {0, 1}
                )

            # 添加负数范围
            if min_num < 0:
                result.update(
                    {
                        -x
                        for x in range(1 if max_num >= 0 else -max_num, -min_num + 1)
                        if x not in primes and x != 1
                    }
                )

            # 如果范围包含0，添加0
            if min_num <= 0 <= max_num:
                result.add(0)

            return result
