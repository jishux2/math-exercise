from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)
from .exercise_widget import ExerciseWidget
from .exercise_settings_dialog import ExerciseSettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数学练习系统")
        self.resize(800, 600)

        # 创建中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建开始按钮
        layout = QVBoxLayout(central_widget)
        start_button = QPushButton("开始练习")
        start_button.setFixedSize(200, 60)
        start_button.clicked.connect(self.startExercise)

        # 设置按钮样式
        start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )

        # 居中显示按钮
        layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()

    def startExercise(self):
        # 显示设置对话框
        dialog = ExerciseSettingsDialog(self)
        if dialog.exec():
            # 获取设置参数
            settings = dialog.get_settings()

            # 创建练习窗口
            exercise_window = QMainWindow(self)
            exercise_window.setWindowTitle("数学练习")
            exercise_window.resize(1000, 600)

            # 创建练习部件
            exercise_widget = ExerciseWidget()
            exercise_window.setCentralWidget(exercise_widget)

            # 设置练习参数
            exercise_widget.difficulty = settings["difficulty"]
            exercise_widget.number_range = settings["number_range"]
            exercise_widget.operators = settings["operators"]
            exercise_widget.operator_types = settings["operator_types"]
            exercise_widget.question_count = settings["question_count"]
            exercise_widget.scoring_strategy = settings["scoring_strategy"]

            try:
                # 初始化练习
                exercise_widget.initExercise()
            except ValueError as e:
                QMessageBox.warning(
                    self,
                    "生成题目失败",
                    f"无法生成符合条件的题目，请尝试调整参数！\n\n具体原因：{str(e)}",
                )
                exercise_window.deleteLater()  # 清理未使用的窗口
                return
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "发生错误",
                    f"初始化练习时发生未知错误！\n\n错误信息：{str(e)}",
                )
                exercise_window.deleteLater()  # 清理未使用的窗口
                return

            # 显示练习窗口
            exercise_window.show()
