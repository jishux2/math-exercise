from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QGraphicsOpacityEffect,
    QScrollArea,
    QFrame,
    QProgressBar,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    Property,
    QRect,
)
from PySide6.QtWidgets import QScroller, QScrollerProperties  # 新增导入
from PySide6.QtGui import QColor, QPalette, QFont
from ..core.exercise import Exercise
from ..models.question import OperatorType
from ..observers.concrete_observers import Student
from ..strategies.concrete_strategies import (
    TimedScoringStrategy,
    AccuracyScoringStrategy,
)
import time


class AnimatedProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self._value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)  # 500ms动画
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

        # 设置样式
        self.setStyleSheet(
            """
            QProgressBar {
                border: none;
                border-radius: 3px;
                background: #f0f0f0;
                height: 6px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 3px;
            }
        """
        )

    def setValue(self, value):
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(value)
        self.animation.start()
        self._value = value


class AnimatedButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.normal_color = QColor("#4CAF50")
        self.hover_color = QColor("#45a049")
        self.pressed_color = QColor("#3d8b40")
        self.disabled_color = QColor("#cccccc")
        self.current_color = self.normal_color

        # 创建属性动画
        self.color_animation = QPropertyAnimation(self, b"background_color")
        self.color_animation.setDuration(200)  # 200ms

        # 设置基础样式
        self._update_style()

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        if enabled:
            self.animate_color(self.normal_color)
        else:
            self.color_animation.stop()
            self.current_color = self.disabled_color
            self._update_style()

    def enterEvent(self, event):
        if self.isEnabled():
            self.animate_color(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isEnabled():
            self.animate_color(self.normal_color)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.isEnabled():
            self.animate_color(self.pressed_color)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            self.animate_color(
                self.hover_color if self.underMouse() else self.normal_color
            )
        super().mouseReleaseEvent(event)

    def animate_color(self, target_color: QColor):
        if not self.isEnabled():
            return
        self.color_animation.stop()
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(target_color)
        self.color_animation.start()
        self.current_color = target_color

    @Property(QColor)
    def background_color(self):
        return self.current_color

    @background_color.setter
    def background_color(self, color: QColor):
        self.current_color = color
        self._update_style()

    def _update_style(self):
        # 更新按钮样式，禁用时忽略所有其他状态
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-size: 15px;
            }}
            QPushButton:disabled {{
                background-color: {self.disabled_color.name()} !important;
            }}
            QPushButton:hover:!disabled {{
                background-color: {self.current_color.name()};
            }}
        """
        )


class QuestionCard(QFrame):
    def __init__(self, question_text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("questionCard")
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # 定义颜色属性
        self._border_color = QColor("#e0e0e0")
        self._background_start_color = QColor("white")
        self._background_end_color = QColor("white")  # 初始时顶部和底部相同
        
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # 创建内容容器
        self.content = QWidget()
        self.content.setObjectName("content")
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        
        # 题目文本
        self.question_label = QLabel(question_text)
        self.question_label.setWordWrap(True)
        content_layout.addWidget(self.question_label)
        
        # 答案输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("输入你的答案")
        self.answer_input.setFixedHeight(40)
        self.submit_button = AnimatedButton("提交")
        self.submit_button.setFixedSize(100, 40)
        input_layout.addWidget(self.answer_input)
        input_layout.addWidget(self.submit_button)
        content_layout.addLayout(input_layout)
        
        # 结果显示（初始隐藏）
        self.result_label = QLabel()
        self.result_label.setVisible(False)
        content_layout.addWidget(self.result_label)
        
        # 添加内容容器到主布局
        self.main_layout.addWidget(self.content)
        
        # 设置透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.content)
        self.opacity_effect.setOpacity(0.0)
        self.content.setGraphicsEffect(self.opacity_effect)

        # 设置样式
        self.setupStyle()
        self.setupAnimations()
        
        # 动画属性
        self._offset = 0.0

    def setupStyle(self):
        self.updateStyle()
        
    def updateStyle(self):
        # 创建渐变背景的CSS
        gradient = f"""
            qlineargradient(
                x1: 0, y1: 0,
                x2: 0, y2: 1,
                stop: 0 {self._background_start_color.name()},
                stop: 0.95 {self._background_end_color.name()},
                stop: 1 {self._background_end_color.darker(110).name()}
            )
        """
        
        self.setStyleSheet(f"""
            #questionCard {{
                background: {gradient};
                border: 1px solid {self._border_color.name()};
                border-radius: 15px;
                margin: 5px;
            }}
            
            QLabel {{
                font-size: 18px;
                color: #333;
                background: transparent;
            }}
            
            QLineEdit {{
                font-size: 16px;
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }}
            
            QLineEdit:focus {{
                border: 2px solid #4CAF50;
            }}
        """)

    def setupAnimations(self):
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        
        # 创建边框颜色动画
        self.border_anim = QPropertyAnimation(self, b"border_color")
        self.border_anim.setDuration(200)
        
        # 创建背景渐变起始色动画
        self.background_start_anim = QPropertyAnimation(self, b"background_start_color")
        self.background_start_anim.setDuration(200)
        
        # 创建背景渐变结束色动画
        self.background_end_anim = QPropertyAnimation(self, b"background_end_color")
        self.background_end_anim.setDuration(200)

    @Property(QColor)
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, color):
        self._border_color = color
        self.updateStyle()

    @Property(QColor)
    def background_start_color(self):
        return self._background_start_color

    @background_start_color.setter
    def background_start_color(self, color):
        self._background_start_color = color
        self.updateStyle()

    @Property(QColor)
    def background_end_color(self):
        return self._background_end_color

    @background_end_color.setter
    def background_end_color(self, color):
        self._background_end_color = color
        self.updateStyle()

    def enterEvent(self, event):
        # 鼠标进入时启动动画
        self.border_anim.setStartValue(self._border_color)
        self.border_anim.setEndValue(QColor("#d0d0d0"))
        self.border_anim.start()
        
        # 背景渐变动画 - 起始色
        self.background_start_anim.setStartValue(self._background_start_color)
        self.background_start_anim.setEndValue(QColor("#ffffff"))
        self.background_start_anim.start()
        
        # 背景渐变动画 - 结束色
        self.background_end_anim.setStartValue(self._background_end_color)
        self.background_end_anim.setEndValue(QColor("#f0f0f0"))
        self.background_end_anim.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        # 鼠标离开时启动动画
        self.border_anim.setStartValue(self._border_color)
        self.border_anim.setEndValue(QColor("#e0e0e0"))
        self.border_anim.start()
        
        # 背景渐变动画 - 起始色
        self.background_start_anim.setStartValue(self._background_start_color)
        self.background_start_anim.setEndValue(QColor("white"))
        self.background_start_anim.start()
        
        # 背景渐变动画 - 结束色
        self.background_end_anim.setStartValue(self._background_end_color)
        self.background_end_anim.setEndValue(QColor("white"))
        self.background_end_anim.start()
        
        super().leaveEvent(event)

    @Property(float)
    def offset(self):
        return self._offset
        
    @offset.setter
    def offset(self, value):
        self._offset = value
        self.updatePosition()
        
    def updatePosition(self):
        self.setContentsMargins(int(self._offset), 0, 0, 0)
        self.update()
        
    def startEntranceAnimation(self):
        self.anim = QPropertyAnimation(self, b"offset")
        self.anim.setDuration(800)
        self.anim.setStartValue(100.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()
        
        self.opacity_anim.setDuration(600)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_anim.start()

    def showResult(self, is_correct: bool, correct_answer: float):
        self.answer_input.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.result_label.setVisible(True)

        if is_correct:
            self.result_label.setText("✓ 回答正确！")
            self.result_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.result_label.setText(f"✗ 正确答案是：{correct_answer}")
            self.result_label.setStyleSheet("color: #f44336; font-weight: bold;")


class ExerciseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.exercise = None
        self.current_question_index = 0
        self.question_cards = []
        self.start_time = 0
        self.setupUI()
        self.initExercise()

        # 设置窗口背景
        self.setStyleSheet(
            """
            ExerciseWidget {
                background: #f5f5f5;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """
        )

    def setupUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # 头部信息区域
        header_layout = QHBoxLayout()

        # 进度显示
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel("完成进度")
        self.progress_label.setStyleSheet("color: #666; font-size: 14px;")
        self.progress_bar = AnimatedProgressBar()
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)

        # 计时器显示
        timer_layout = QVBoxLayout()
        self.timer_label = QLabel("用时")
        self.timer_label.setStyleSheet("color: #666; font-size: 14px;")
        self.time_display = QLabel("0:00")
        self.time_display.setStyleSheet(
            "color: #333; font-size: 18px; font-weight: bold;"
        )
        timer_layout.addWidget(self.timer_label)
        timer_layout.addWidget(self.time_display)

        header_layout.addLayout(progress_layout)
        header_layout.addStretch()
        header_layout.addLayout(timer_layout)

        self.main_layout.addLayout(header_layout)

        # 创建内容容器
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")

        # 使用QVBoxLayout，并设置合适的边距
        self.questions_container = QVBoxLayout(self.content_widget)
        self.questions_container.setSpacing(20)
        self.questions_container.setContentsMargins(
            20, 20, 20, 20
        )  # 给阴影留出足够空间
        self.questions_container.setAlignment(Qt.AlignTop)

        # 设置滚动区域
        self.scroll_area = QScrollArea()  # 将scroll_area设为实例变量
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollArea > QWidget {
                background: transparent;
            }
        """)
        
        self.main_layout.addWidget(self.scroll_area)

        # 设置计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimer)
        self.timer.start(1000)

    def addQuestionCard(self, question_text: str):
        # 获取当前卡片的索引
        current_index = len(self.question_cards)

        card = QuestionCard(question_text)
        # 使用固定值捕获当前索引
        card.submit_button.clicked.connect(
            lambda checked: self.handleAnswer(current_index)
        )
        card.answer_input.returnPressed.connect(
            lambda idx=current_index: self.handleAnswer(idx)
        )

        # 创建动画
        self.questions_container.addWidget(card)
        self.question_cards.append(card)

        # 启动入场动画
        QTimer.singleShot(50, card.startEntranceAnimation)  # 延迟一下启动动画

        # 设置定时器等待动画完成后滚动到底部
        QTimer.singleShot(100, self.scrollToBottom)

    def scrollToBottom(self):
        # 使用动画滚动到底部
        scroll_bar = self.scroll_area.verticalScrollBar()
        current_value = scroll_bar.value()
        max_value = scroll_bar.maximum()
        
        # 创建滚动动画
        self.scroll_animation = QPropertyAnimation(scroll_bar, b"value")
        self.scroll_animation.setDuration(300)  # 300ms的滚动动画
        self.scroll_animation.setStartValue(current_value)
        self.scroll_animation.setEndValue(max_value)
        self.scroll_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.scroll_animation.start()

    def handleAnswer(self, question_index: int):
        print(f"question_index: {question_index}")
        if question_index >= len(self.question_cards):
            return

        card = self.question_cards[question_index]

        try:
            answer = float(card.answer_input.text())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字！")
            return

        # 计算耗时
        current_time = time.time()
        time_spent = int(current_time - self.start_time)

        # 提交答案并显示结果
        is_correct = self.exercise.submit_answer(question_index, answer, time_spent)

        card.showResult(is_correct, self.exercise.questions[question_index].answer)

        # 更新进度
        progress = (question_index + 1) / len(self.exercise.questions) * 100
        self.progress_bar.setValue(progress)

        # 如果还有下一题，添加新卡片
        if question_index + 1 < len(self.exercise.questions):
            self.addQuestionCard(self.exercise.questions[question_index + 1].content)
        else:
            # 练习完成
            final_score = self.exercise.submit_exercise()
            QMessageBox.information(
                self,
                "练习完成",
                f"太棒了！你的最终得分是：{final_score}分\n"
                f"用时：{self.formatTime(time_spent)}",
            )
            self.resetExercise()

    def updateTimer(self):
        if self.current_question_index < len(self.exercise.questions):
            elapsed_time = int(time.time() - self.start_time)
            self.time_display.setText(self.formatTime(elapsed_time))

    def formatTime(self, seconds: int) -> str:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def initExercise(self):
        # 清除现有题目
        for card in self.question_cards:
            card.deleteLater()
        self.question_cards.clear()

        # 重置布局
        while self.questions_container.count():
            item = self.questions_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 初始化练习
        self.exercise = Exercise("简单", (1, 100))
        self.exercise.add_observer(Student("测试用户"))
        self.exercise.set_scoring_strategy(TimedScoringStrategy())

        # 生成题目
        self.exercise.generate_questions(
            [OperatorType.ADDITION, OperatorType.SUBTRACTION], count=5
        )

        # 重置进度条
        self.progress_bar.setValue(0)

        # 显示第一题
        self.addQuestionCard(self.exercise.questions[0].content)

        # 重置计时器
        self.start_time = time.time()

    def resetExercise(self):
        self.current_question_index = 0
        self.initExercise()
