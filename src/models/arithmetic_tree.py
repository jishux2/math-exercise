"""
本模块实现了算术表达式的树形表示：
1. ArithmeticNode: 表达式树的节点类
   - 存储操作数、运算符和树形结构
   - 每个节点的操作数是其子树计算的结果
2. ArithmeticTree: 表达式树类
   - 实现了表达式的存储和转换
   - 处理运算符优先级和括号
   - 通过中序遍历生成完整表达式

该模块为题目生成提供了核心的数据结构支持，
确保生成的表达式结构正确、运算符优先级恰当。
"""

from dataclasses import dataclass  # 导入dataclass装饰器，用于创建数据类
from typing import Optional  # 导入Optional类型，用于表示可选值
from .question import OperatorType  # 从同目录下的question模块导入OperatorType枚举类


@dataclass  # 使用dataclass装饰器，自动生成__init__等基本方法
class ArithmeticNode:
    """算术表达式树的节点类

    每个节点存储：
    1. operand: 该节点代表的子树的计算结果
    2. operator: 用于计算当前节点的运算符（如果是非叶节点）
    3. left_node和right_node: 左右子节点
    4. parent_node: 父节点的引用，用于处理运算符优先级
    """

    operand: int  # 存储该节点的计算结果值
    operator: Optional[OperatorType] = None  # 当前节点的运算符，叶节点为None
    left_node: Optional["ArithmeticNode"] = None  # 左子节点
    right_node: Optional["ArithmeticNode"] = None  # 右子节点
    parent_node: Optional["ArithmeticNode"] = None  # 父节点引用

    def set_left_node(self, node: "ArithmeticNode"):
        """设置左子节点，同时建立父子关系"""
        node.parent_node = self  # 设置子节点的父节点引用
        self.left_node = node  # 设置当前节点的左子节点引用

    def set_right_node(self, node: "ArithmeticNode"):
        """设置右子节点，同时建立父子关系"""
        node.parent_node = self  # 设置子节点的父节点引用
        self.right_node = node  # 设置当前节点的右子节点引用


class ArithmeticTree:
    """算术表达式树类

    特点：
    1. 每个节点存储的operand是该节点下子树的计算结果
    2. 非叶节点的operand是对其左右子节点operand进行operator运算的结果
    3. 叶节点直接存储输入的数值，没有operator
    """

    def __init__(self):
        """初始化空的表达式树"""
        self.root = None

    def is_empty(self):
        """判断树是否为空"""
        return self.root is None

    def get_arithmetic(self) -> str:
        """生成表示整个算术表达式的字符串，通过中序遍历实现"""
        return self._inorder(self.root)

    def _inorder(self, node: ArithmeticNode) -> str:
        """递归进行中序遍历，生成带正确括号的表达式字符串

        算法：
        1. 对于叶节点，直接返回其操作数
        2. 对于非叶节点，递归处理左子树、当前运算符、右子树
        3. 根据运算符优先级规则添加必要的括号

        Args:
            node: 当前处理的节点

        Returns:
            表示当前子树对应算术表达式的字符串
        """
        # 空节点返回空字符串
        if node is None:
            return ""

        # 叶节点：如果是负数加括号，否则直接转字符串
        if node.left_node is None and node.right_node is None:
            return f"({node.operand})" if node.operand < 0 else str(node.operand)

        # 递归生成左子树表达式
        left = self._inorder(node.left_node)
        # 获取当前节点的运算符
        operator = node.operator.value
        # 递归生成右子树表达式
        right = self._inorder(node.right_node)

        # 判断是否需要给当前表达式加括号
        needs_parentheses = node.parent_node is not None and self._needs_parentheses(
            node.operator, node.parent_node.operator
        )

        # 根据需要返回带括号或不带括号的表达式
        if needs_parentheses:
            return f"({left} {operator} {right})"
        return f"{left} {operator} {right}"

    def _needs_parentheses(
        self, current_op: OperatorType, parent_op: OperatorType
    ) -> bool:
        """判断当前运算是否需要括号以保持正确的计算顺序

        规则：
        1. 当前运算符优先级低于父运算符时需要括号
        2. 同级运算符中，减法和除法需要括号（因为不满足结合律）

        Args:
            current_op: 当前运算符
            parent_op: 父节点的运算符

        Returns:
            bool: 是否需要括号
        """
        if current_op is None or parent_op is None:
            return False

        # 定义运算符优先级
        priorities = {
            OperatorType.ADDITION: 1,  # 加法优先级为1
            OperatorType.SUBTRACTION: 1,  # 减法优先级为1
            OperatorType.MULTIPLICATION: 2,  # 乘法优先级为2
            OperatorType.DIVISION: 2,  # 除法优先级为2
        }

        # 当前运算符优先级低于父运算符时需要括号
        # 如：(a + b) * c
        if priorities[current_op] < priorities[parent_op]:
            return True

        # 同级运算中，减法和除法需要括号
        # 如：(a - b) - c，因为a - (b - c)结果不同
        # 如：(a ÷ b) ÷ c，因为a ÷ (b ÷ c)结果不同
        if priorities[current_op] == priorities[parent_op]:
            if current_op in (OperatorType.SUBTRACTION, OperatorType.DIVISION):
                return True

        return False
