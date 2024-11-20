# src/models/arithmetic_tree.py

from dataclasses import dataclass
from typing import Optional
from .question import OperatorType


@dataclass
class ArithmeticNode:
    operand: int
    operator: Optional[OperatorType] = None
    left_node: Optional["ArithmeticNode"] = None
    right_node: Optional["ArithmeticNode"] = None
    parent_node: Optional["ArithmeticNode"] = None

    def set_left_node(self, node: "ArithmeticNode"):
        node.parent_node = self
        self.left_node = node

    def set_right_node(self, node: "ArithmeticNode"):
        node.parent_node = self
        self.right_node = node


class ArithmeticTree:
    def __init__(self):
        self.root = None

    def is_empty(self):
        return self.root is None

    def get_arithmetic(self) -> str:
        """中序遍历生成算式"""
        return self._inorder(self.root)

    def _inorder(self, node: ArithmeticNode) -> str:
        if node is None:
            return ""

        # 如果是叶节点（没有子节点）
        if node.left_node is None and node.right_node is None:
            # 如果是负数，加括号
            return f"({node.operand})" if node.operand < 0 else str(node.operand)

        # 递归处理左右子树
        left = self._inorder(node.left_node)
        operator = node.operator.value
        right = self._inorder(node.right_node)

        # 根据运算符优先级决定是否需要括号
        needs_parentheses = node.parent_node is not None and self._needs_parentheses(
            node.operator, node.parent_node.operator
        )

        if needs_parentheses:
            return f"({left} {operator} {right})"
        return f"{left} {operator} {right}"

    def _needs_parentheses(
        self, current_op: OperatorType, parent_op: OperatorType
    ) -> bool:
        """判断是否需要括号"""
        if current_op is None or parent_op is None:
            return False

        # 定义运算符优先级
        priorities = {
            OperatorType.ADDITION: 1,
            OperatorType.SUBTRACTION: 1,
            OperatorType.MULTIPLICATION: 2,
            OperatorType.DIVISION: 2,
        }

        # 如果当前运算符优先级低于父运算符，需要括号
        if priorities[current_op] < priorities[parent_op]:
            return True

        # 如果是同级运算符，减法和除法需要括号（因为不满足结合律）
        if priorities[current_op] == priorities[parent_op]:
            if current_op in (OperatorType.SUBTRACTION, OperatorType.DIVISION):
                return True

        return False
