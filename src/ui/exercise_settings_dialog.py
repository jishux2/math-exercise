from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QDialogButtonBox,
    QGroupBox,
)
from ..models.question import DifficultyLevel, OperatorType
from ..strategies.concrete_strategies import (
    AccuracyScoringStrategy,
    TimedScoringStrategy,
)


class ExerciseSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("练习设置")
        self.resize(400, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 基本设置
        basic_group = QGroupBox("基本设置")
        form_layout = QFormLayout()

        # 难度选择
        self.difficulty_combo = QComboBox()
        for level in DifficultyLevel:
            self.difficulty_combo.addItem(level.value, level)

        # 数值范围
        range_layout = QHBoxLayout()
        self.min_spin = QSpinBox()
        self.min_spin.setRange(-1000, 1000)
        self.min_spin.setValue(-100)
        self.max_spin = QSpinBox()
        self.max_spin.setRange(-1000, 1000)
        self.max_spin.setValue(100)
        range_layout.addWidget(self.min_spin)
        range_layout.addWidget(QLabel("到"))
        range_layout.addWidget(self.max_spin)

        # 题目数量
        self.question_count_spin = QSpinBox()
        self.question_count_spin.setRange(1, 100)
        self.question_count_spin.setValue(5)

        form_layout.addRow("难度：", self.difficulty_combo)
        form_layout.addRow("数值范围：", range_layout)
        form_layout.addRow("题目数量：", self.question_count_spin)
        basic_group.setLayout(form_layout)

        # 运算符选择
        operator_group = QGroupBox("运算类型")
        operator_layout = QVBoxLayout()

        self.operator_checks = {}
        for op in OperatorType:
            checkbox = QCheckBox(op.value)
            checkbox.setChecked(True)
            self.operator_checks[op] = checkbox
            operator_layout.addWidget(checkbox)

        operator_group.setLayout(operator_layout)

        # 计分策略
        scoring_group = QGroupBox("计分策略")
        scoring_layout = QVBoxLayout()

        self.accuracy_radio = QCheckBox("仅计算正确率")
        self.accuracy_radio.setChecked(True)
        self.timed_radio = QCheckBox("计入答题用时")
        scoring_layout.addWidget(self.accuracy_radio)
        scoring_layout.addWidget(self.timed_radio)

        # 添加"权重设置"子表单（仅当选择"计入答题用时"时显示）
        weights_layout = QFormLayout()

        self.accuracy_weight = QSpinBox()
        self.accuracy_weight.setRange(1, 99)
        self.accuracy_weight.setValue(70)
        self.accuracy_weight.setSuffix("%")

        self.time_weight = QSpinBox()
        self.time_weight.setRange(1, 99)
        self.time_weight.setValue(30)
        self.time_weight.setSuffix("%")

        weights_layout.addRow("正确率权重：", self.accuracy_weight)
        weights_layout.addRow("时间权重：", self.time_weight)

        # 添加权重变化的连接
        self.accuracy_weight.valueChanged.connect(self._on_accuracy_weight_changed)
        self.time_weight.valueChanged.connect(self._on_time_weight_changed)
        
        # 初始时隐藏权重设置
        self.weights_group = QGroupBox("权重设置")
        self.weights_group.setLayout(weights_layout)
        self.weights_group.setVisible(False)

        scoring_layout.addWidget(self.weights_group)
        scoring_group.setLayout(scoring_layout)

        # 设置互斥
        self.accuracy_radio.toggled.connect(
            lambda checked: self.timed_radio.setChecked(not checked)
        )
        self.timed_radio.toggled.connect(
            lambda checked: self.accuracy_radio.setChecked(not checked)
        )
        self.timed_radio.toggled.connect(self.weights_group.setVisible)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate)
        button_box.rejected.connect(self.reject)

        # 添加所有组件到主布局
        layout.addWidget(basic_group)
        layout.addWidget(operator_group)
        layout.addWidget(scoring_group)
        layout.addWidget(button_box)

    def _on_accuracy_weight_changed(self, value):
        """当正确率权重改变时，同步更新时间权重"""
        # 阻止信号以避免循环
        self.time_weight.blockSignals(True)
        self.time_weight.setValue(100 - value)
        self.time_weight.blockSignals(False)

    def _on_time_weight_changed(self, value):
        """当时间权重改变时，同步更新正确率权重"""
        # 阻止信号以避免循环
        self.accuracy_weight.blockSignals(True)
        self.accuracy_weight.setValue(100 - value)
        self.accuracy_weight.blockSignals(False)
        
    def validate(self):
        """验证输入参数"""
        # 检查是否至少选择了一个运算符
        if not any(check.isChecked() for check in self.operator_checks.values()):
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "输入错误", "请至少选择一种运算类型！")
            return

        # 检查数值范围
        if self.min_spin.value() >= self.max_spin.value():
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "输入错误", "最小值必须小于最大值！")
            return

        # 检查权重和（如果启用）
        if self.timed_radio.isChecked():
            total_weight = self.accuracy_weight.value() + self.time_weight.value()
            if total_weight != 100:
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.warning(self, "输入错误", "权重之和必须等于100%！")
                return

        self.accept()

    def get_settings(self):
        """获取设置参数"""
        operators = [
            op for op, check in self.operator_checks.items() if check.isChecked()
        ]
        operator_types = [op.value for op in operators]  # 字符串形式的运算符

        if self.timed_radio.isChecked():
            scoring_strategy = TimedScoringStrategy(
                time_weight=self.time_weight.value() / 100,
                accuracy_weight=self.accuracy_weight.value() / 100,
            )
        else:
            scoring_strategy = AccuracyScoringStrategy()

        return {
            "difficulty": self.difficulty_combo.currentData(),
            "number_range": (self.min_spin.value(), self.max_spin.value()),
            "question_count": self.question_count_spin.value(),
            "operators": operators,
            "operator_types": operator_types,  # 添加字符串形式的运算符列表
            "scoring_strategy": scoring_strategy,
        }
