from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from .exercise_widget import ExerciseWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数学练习系统")
        self.resize(1000, 600)
        
        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加练习界面
        self.exercise_widget = ExerciseWidget()
        layout.addWidget(self.exercise_widget)
