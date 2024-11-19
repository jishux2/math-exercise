import json
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class QuestionRecord:
    content: str
    user_answer: float
    correct_answer: float
    is_correct: bool
    time_spent: int


class ExerciseRecord:
    def __init__(self, difficulty: str, number_range: tuple, operator_types: List[str]):
        self.difficulty = difficulty
        self.number_range = number_range
        self.operator_types = operator_types
        self.questions: List[QuestionRecord] = []
        self.total_time = 0
        self.final_score = 0
        self.timestamp = datetime.now()

    def add_question_record(self, question: QuestionRecord):
        self.questions.append(question)

    def to_prompt_message(self) -> str:
        """转换为发送给AI的消息格式"""
        questions_info = []
        for idx, q in enumerate(self.questions, 1):
            question_text = f"""第{idx}题：{q.content}
用户答案：{q.user_answer}
正确答案：{q.correct_answer}
是否正确：{'是' if q.is_correct else '否'}
用时：{q.time_spent}秒"""
            questions_info.append(question_text)

        separator = "-" * 30
        questions_section = f"\n{separator}\n".join(questions_info)

        prompt = f"""你现在是一位经验丰富的小学数学老师。请针对以下练习情况给出评语和建议：

练习信息：
难度级别：{self.difficulty}
数值范围：{self.number_range[0]}到{self.number_range[1]}
运算类型：{', '.join(self.operator_types)}
总用时：{self.total_time}秒
最终得分：{self.final_score}

具体题目记录：
{separator}
{questions_section}
{separator}

请从以下几个方面进行点评：
1. 整体表现评价
2. 存在的问题分析
3. 针对性的改进建议

请用友善、鼓励的语气，重点强调学生的进步空间。"""

        return prompt
