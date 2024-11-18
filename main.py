import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 测试单参数函数
        btn1 = QPushButton("测试1：单参数函数")
        btn1.setCheckable(True)
        btn1.clicked.connect(self.singleArg)
        layout.addWidget(btn1)

        # 测试双参数函数，这样会报错
        btn2 = QPushButton("测试2：双参数函数（会报错）")
        btn2.setCheckable(True)
        try:
            btn2.clicked.connect(self.doubleArg)
            btn2.setText("测试2：竟然没报错！")
        except TypeError as e:
            btn2.setText(f"测试2：报错 - {str(e)}")
        layout.addWidget(btn2)

        # 使用clicked[bool]的正确方式
        btn3 = QPushButton("测试3：使用clicked[bool]")
        btn3.setCheckable(True)
        btn3.clicked[bool].connect(self.doubleArg)
        layout.addWidget(btn3)

        # 使用lambda，方式1
        btn4 = QPushButton("测试4：lambda方式1")
        btn4.setCheckable(True)
        current_index = 42  # 模拟你原始代码中的current_index
        btn4.clicked.connect(
            lambda checked=False, idx=current_index: self.handleAnswer(idx)
        )
        layout.addWidget(btn4)

        # 使用lambda，方式2
        btn5 = QPushButton("测试5：lambda方式2")
        btn5.setCheckable(True)
        btn5.clicked.connect(lambda checked: self.handleAnswer(current_index))
        layout.addWidget(btn5)

    def singleArg(self, checked):
        print(f"singleArg: checked = {checked}")

    def doubleArg(self, checked, value=10):
        print(f"doubleArg: checked = {checked}, value = {value}")

    def handleAnswer(self, idx):
        print(f"handleAnswer: idx = {idx}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWidget()
    window.show()
    sys.exit(app.exec())
