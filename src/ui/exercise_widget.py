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
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QStatusBar,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    Property,
    QRect,
    QParallelAnimationGroup,
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


class AnimatedProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self._value = 0

        # 创建布局，添加适当的边距以显示阴影
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 10)  # 底部边距稍大一些以容纳阴影

        # 创建实际的进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background-color: #f5f5f5;
                min-height: 20px;
                max-height: 20px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3,
                    stop:0.5 #03A9F4,
                    stop:1 #00BCD4
                );
            }
            """
        )

        # 创建阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.progress_bar.setGraphicsEffect(shadow)

        # 创建百分比标签
        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignCenter)
        self.percent_label.setStyleSheet(
            """
            QLabel {
                color: #666;
                font-size: 10px;
                font-weight: bold;
                background: transparent;
            }
            """
        )

        # 将进度条和标签添加到布局中
        layout.addWidget(self.progress_bar)

        # 创建动画组
        self.animation_group = QParallelAnimationGroup(self)

        # 进度条动画
        self.progress_animation = QPropertyAnimation(self, b"value")
        self.progress_animation.setDuration(500)
        self.progress_animation.setEasingCurve(QEasingCurve.OutQuad)

        # 文字动画
        self.text_animation = QPropertyAnimation(self, b"textValue")
        self.text_animation.setDuration(500)
        self.text_animation.setEasingCurve(QEasingCurve.OutQuad)

        # 将两个动画添加到动画组
        self.animation_group.addAnimation(self.progress_animation)
        self.animation_group.addAnimation(self.text_animation)

        # 确保标签位于进度条上方居中
        self.percent_label.setParent(self.progress_bar)
        self.progress_bar.resizeEvent = self.updateLabelPosition

    def updateLabelPosition(self, event):
        # 确保标签始终居中显示在进度条上
        self.percent_label.setGeometry(self.progress_bar.rect())

    @Property(float)
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.progress_bar.setValue(int(val))

    @Property(float)
    def textValue(self):
        return float(self.percent_label.text().rstrip("%"))

    @textValue.setter
    def textValue(self, val):
        self.percent_label.setText(f"{int(val)}%")

    def setValue(self, value):
        # 设置动画的起始和结束值
        self.progress_animation.setStartValue(self.value)
        self.progress_animation.setEndValue(value)

        self.text_animation.setStartValue(self.textValue)
        self.text_animation.setEndValue(value)

        # 启动动画组
        self.animation_group.start()


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

        self.setStyleSheet(
            f"""
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
        """
        )

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


class QuestionListItem(QListWidgetItem):
    def __init__(self, question_text: str, index: int):
        super().__init__()
        self.question_text = question_text
        self.index = index
        self.updateDisplay()

    def updateDisplay(self, status: str = "未开始"):
        # 状态对应的样式
        status_styles = {
            "未开始": {"color": "#909090", "prefix": "□"},
            "当前": {"color": "#2196F3", "prefix": "▶"},
            "正确": {"color": "#4CAF50", "prefix": "✓"},
            "错误": {"color": "#f44336", "prefix": "✗"},
        }

        style = status_styles.get(status, status_styles["未开始"])
        self.setText(f"{style['prefix']} 第{self.index + 1}题：{self.question_text}")
        self.setForeground(QColor(style["color"]))


class ExerciseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.exercise = None
        self.current_question_index = 0
        self.question_cards = []
        self.start_time = 0
        self.setupUI()
        self.initExercise()

    def setupUI(self):
        # 主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # 左侧区域
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 添加标题标签
        title_label = QLabel("题目列表")
        title_label.setStyleSheet(
            """
            QLabel {
                color: #333;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 5px;
            }
        """
        )
        left_layout.addWidget(title_label)

        # 左侧题目列表
        self.question_list = QListWidget()
        self.question_list.setMinimumWidth(200)  # 设置最小宽度
        self.question_list.setStyleSheet(
            """
            QListWidget {
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #e9e9e9;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976D2;
            }
        """
        )
        self.question_list.itemClicked.connect(self.onQuestionItemClicked)

        # 为左侧容器创建阴影效果
        left_shadow = QGraphicsDropShadowEffect(self)
        left_shadow.setBlurRadius(15)
        left_shadow.setXOffset(0)
        left_shadow.setYOffset(3)
        left_shadow.setColor(QColor(0, 0, 0, 30))
        left_container.setGraphicsEffect(left_shadow)

        left_layout.addWidget(self.question_list)

        # 右侧区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # 创建分割器
        self.splitter = QSplitter(Qt.Vertical)
        # 设置分割器的手柄的宽度为10像素
        self.splitter.setHandleWidth(10)
        # 设置分割器中的框架不可以被折叠
        self.splitter.setChildrenCollapsible(False)

        # 上部分：题目区域
        upper_container = QWidget()
        upper_container.setMinimumHeight(400)  # 设置最小高度
        upper_layout = QVBoxLayout(upper_container)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(0)

        # 创建内容容器
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")

        # 设置内容容器的布局
        self.questions_container = QVBoxLayout(self.content_widget)
        self.questions_container.setSpacing(20)
        self.questions_container.setContentsMargins(20, 20, 20, 20)
        self.questions_container.setAlignment(Qt.AlignTop)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setStyleSheet(
            """
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
        """
        )

        # 在setupUI中添加以下代码
        scroller = QScroller.scroller(self.scroll_area.viewport())
        scroller.grabGesture(
            self.scroll_area.viewport(), QScroller.LeftMouseButtonGesture
        )

        # 设置滚动属性
        scroll_props = scroller.scrollerProperties()
        scroll_props.setScrollMetric(
            QScrollerProperties.VerticalOvershootPolicy,
            QScrollerProperties.OvershootAlwaysOff,
        )
        scroller.setScrollerProperties(scroll_props)

        # 将滚动区域添加到上部分容器
        upper_layout.addWidget(self.scroll_area)

        # 下部分：日志区域
        self.log_container = QWidget()
        self.log_container.setMinimumHeight(150)  # 设置最小高度
        self.log_container.setMaximumHeight(200)  # 设置最大高度限制
        log_layout = QVBoxLayout(self.log_container)

        # 为日志容器创建阴影效果
        log_shadow = QGraphicsDropShadowEffect(self)
        log_shadow.setBlurRadius(15)
        log_shadow.setXOffset(0)
        log_shadow.setYOffset(3)
        log_shadow.setColor(QColor(0, 0, 0, 30))
        self.log_container.setGraphicsEffect(log_shadow)

        # 日志标题栏
        log_header = QWidget()
        log_header_layout = QHBoxLayout(log_header)
        log_header_layout.setContentsMargins(0, 0, 0, 0)

        log_label = QLabel("运行日志")
        log_label.setStyleSheet("color: #666; font-weight: bold;")
        self.stop_button = QPushButton("停止")
        self.stop_button.setFixedSize(60, 24)
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #e53935;
            }
            QPushButton:pressed {
                background: #d32f2f;
            }
        """
        )

        log_header_layout.addWidget(log_label)
        log_header_layout.addStretch()
        log_header_layout.addWidget(self.stop_button)

        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, Monaco, monospace;
                font-size: 13px;
            }
        """
        )

        log_layout.addWidget(log_header)
        log_layout.addWidget(self.log_text)

        # 将上下部分添加到分割器
        self.splitter.addWidget(upper_container)
        self.splitter.addWidget(self.log_container)

        # 设置分割器的伸缩因子
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)

        # 替换原来的底部状态栏
        self.status_bar = QStatusBar()

        # 创建永久小部件用于显示进度
        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(5, 0, 5, 0)

        self.progress_label = QLabel("完成进度")
        self.progress_label.setStyleSheet("color: #666; font-size: 14px;")
        self.progress_bar = AnimatedProgressBar()

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)

        # 创建用于显示时间的小部件
        timer_widget = QWidget()
        timer_layout = QHBoxLayout(timer_widget)
        timer_layout.setContentsMargins(5, 0, 5, 0)

        self.timer_label = QLabel("用时")
        self.timer_label.setStyleSheet("color: #666; font-size: 14px;")
        self.time_display = QLabel("0:00")
        self.time_display.setStyleSheet(
            "color: #333; font-size: 14px; font-weight: bold;"
        )

        timer_layout.addWidget(self.timer_label)
        timer_layout.addWidget(self.time_display)

        self.status_bar.addPermanentWidget(progress_widget, stretch=1)
        self.status_bar.addPermanentWidget(timer_widget)

        # 将分割器和状态栏添加到右侧布局
        right_layout.addWidget(self.splitter, stretch=1)
        right_layout.addWidget(self.status_bar)

        # 将左侧列表和右侧区域添加到主布局
        self.main_layout.addWidget(left_container, stretch=1)
        self.main_layout.addWidget(right_widget, stretch=6)

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
        # 设置焦点到输入框
        QTimer.singleShot(100, card.answer_input.setFocus)

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
        list_item = self.question_list.item(question_index)

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
        list_item.updateDisplay("正确" if is_correct else "错误")

        # 更新进度
        progress = (question_index + 1) / len(self.exercise.questions) * 100
        self.progress_bar.setValue(progress)

        # 如果还有下一题，添加新卡片
        if question_index + 1 < len(self.exercise.questions):
            self.addQuestionCard(self.exercise.questions[question_index + 1].content)
            next_list_item = self.question_list.item(question_index + 1)
            next_list_item.updateDisplay("当前")
            self.question_list.setCurrentItem(next_list_item)
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
        self.question_list.clear()
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

        for i, question in enumerate(self.exercise.questions):
            # 添加到列表
            list_item = QuestionListItem(question.content, i)
            self.question_list.addItem(list_item)

        # 设置第一题为当前题目
        first_item = self.question_list.item(0)
        first_item.updateDisplay("当前")
        self.question_list.setCurrentItem(first_item)

        # 重置进度条
        self.progress_bar.setValue(0)

        # 显示第一题
        self.addQuestionCard(self.exercise.questions[0].content)

        # 重置计时器
        self.start_time = time.time()

    def onQuestionItemClicked(self, item: QuestionListItem):
        if 0 <= item.index < len(self.question_cards):
            card = self.question_cards[item.index]
            # 将目标卡片滚动到顶部
            self.scroll_area.verticalScrollBar().setValue(
                card.pos().y() - self.questions_container.contentsMargins().top()
            )

    def resetExercise(self):
        self.current_question_index = 0
        self.initExercise()
