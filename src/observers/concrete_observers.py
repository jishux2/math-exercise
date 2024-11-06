from .exercise_observer import ExerciseObserver, ExerciseStatus

class Student(ExerciseObserver):
    def __init__(self, name: str):
        self.name = name
    
    def on_exercise_state_changed(self, status: ExerciseStatus):
        print(f"学生{self.name}收到通知：练习状态变更为{status.value}")

class Teacher(ExerciseObserver):
    def __init__(self, name: str):
        self.name = name
    
    def on_exercise_state_changed(self, status: ExerciseStatus):
        print(f"教师{self.name}收到通知：练习状态变更为{status.value}")

class Parent(ExerciseObserver):
    def __init__(self, name: str):
        self.name = name
    
    def on_exercise_state_changed(self, status: ExerciseStatus):
        print(f"家长{self.name}收到通知：练习状态变更为{status.value}")
