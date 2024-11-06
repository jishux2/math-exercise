from src.core.exercise import Exercise
from src.models.question import OperatorType
from src.observers.concrete_observers import Student, Teacher, Parent
from src.strategies.concrete_strategies import TimedScoringStrategy, AccuracyScoringStrategy
import random

def main():
    # 创建练习
    exercise = Exercise("简单", (1, 100))
    
    # 添加观察者
    student = Student("小明")
    teacher = Teacher("张老师")
    parent = Parent("小明妈妈")
    
    exercise.add_observer(student)
    exercise.add_observer(teacher)
    exercise.add_observer(parent)
    
    # 生成题目
    exercise.generate_questions(
        [OperatorType.ADDITION, OperatorType.SUBTRACTION], 
        count=5
    )
    
    # 设置计分策略
    exercise.set_scoring_strategy(AccuracyScoringStrategy())
    
    # 模拟答题
    for i, question in enumerate(exercise.questions):
        print(f"题目 {i+1}: {question.content}")
        # 模拟用户输入答案
        user_answer = float(input("请输入答案: "))
        exercise.submit_answer(i, user_answer, time_spent=random.randint(20, 60))
    
    # 提交练习
    final_score = exercise.submit_exercise()
    print(f"最终得分：{final_score}")

if __name__ == "__main__":
    main()
