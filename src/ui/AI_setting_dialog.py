from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)


class AISettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(600, 100)
        self.setWindowTitle("AI点评设置")
        self.setModal(True)

        layout = QFormLayout(self)

        # 添加输入框
        self.pb_input = QLineEdit()
        self.pb_input.setPlaceholderText("输入p-b token")
        self.pb_input.setText("0dPL9p66HeK2FZUORwP8YQ%3D%3D")  # 默认值

        self.plat_input = QLineEdit()
        self.plat_input.setPlaceholderText("输入p-lat token")
        self.plat_input.setText(
            "39WqZnPmcEx9IL82sNbiwQYl2Od0dGWnx%2F%2BnmxjBzQ%3D%3D"
        )  # 默认值

        layout.addRow("p-b:", self.pb_input)
        layout.addRow("p-lat:", self.plat_input)

        # 添加按钮
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.validate)
        self.button_box.rejected.connect(self.reject)

        layout.addRow(self.button_box)

    def validate(self):
        """验证输入的token"""
        pb = self.pb_input.text().strip()
        plat = self.plat_input.text().strip()

        if not pb or not plat:
            QMessageBox.warning(self, "输入错误", "请输入有效的token！")
            return

        self.accept()
