"""
题目模型模块

本模块定义了与数学题目相关的基本数据结构：
1. DifficultyLevel: 题目难度级别的枚举
2. OperatorType: 运算符类型的枚举
3. Question: 题目类，包含题目内容、答案、使用的运算符等信息

这些类为整个系统提供了基础的数据模型，被其他模块广泛使用。
"""

from dataclasses import dataclass  # 导入dataclass装饰器，用于创建数据类
from enum import Enum  # 导入Enum用于创建枚举类
from typing import Optional, List  # 导入类型提示所需的类


class DifficultyLevel(Enum):
    """题目难度级别的枚举类"""

    EASY = "简单"  # 简单难度
    MEDIUM = "中等"  # 中等难度
    HARD = "困难"  # 困难难度


class OperatorType(Enum):
    """运算符类型的枚举类"""

    ADDITION = "+"  # 加法运算符
    SUBTRACTION = "-"  # 减法运算符
    MULTIPLICATION = "*"  # 乘法运算符
    DIVISION = "/"  # 除法运算符


@dataclass
class Question:
    """题目类，存储题目的各种信息

    Attributes:
        content: 题目内容（算术表达式字符串）
        answer: 正确答案
        operator_types: 题目中包含的运算符类型列表
        user_answer: 用户的答案，可选
    """

    content: str  # 题目内容，如"2 + 3 * 4"
    answer: float  # 正确答案
    operator_types: List[OperatorType]  # 题目中使用的运算符列表
    user_answer: Optional[float] = None  # 用户答案，初始为None

    def check_answer(self) -> bool:
        """检查用户答案是否正确

        使用浮点数比较时考虑精度误差，允许0.001的误差范围

        Returns:
            bool: 用户答案是否正确
        """
        return abs(self.answer - self.user_answer) < 0.001
