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
    QApplication,
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
    Signal,
    QObject,
    QEvent,
)
from PySide6.QtWidgets import QScroller, QScrollerProperties  # 新增导入
from PySide6.QtGui import QColor, QPalette, QFont, QTextCursor
from ..core.exercise import Exercise
from ..core.exercise_record import ExerciseRecord, QuestionRecord
from ..models.question import OperatorType, DifficultyLevel
from ..observers.concrete_observers import Student
from ..strategies.concrete_strategies import (
    TimedScoringStrategy,
    AccuracyScoringStrategy,
)
from .preview_window import PreviewWindow
from .AI_setting_dialog import AISettingsDialog
from poe_api_wrapper import PoeApi
import time
from threading import Thread, Event


class UIUpdateSignals(QObject):
    client_init_success = Signal(object)  # 传递初始化后的client对象
    client_init_failure = Signal(str)  # 传递错误信息
    append_text = Signal(str)  # 用于更新文本
    clear_text = Signal()  # 用于清除文本


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
        self.preview_window = None  # 添加成员变量
        self.poe_client = None  # 初始化为None
        self.exercise_record = None
        self.ignore_ai_toggle = False  # 添加这个标志
        self.feedback_thread = None
        self.stop_event = Event()

        # 添加练习参数成员变量
        self.difficulty = None
        self.number_range = None
        self.operators = None
        self.operator_types = None
        self.question_count = None
        self.scoring_strategy = None
        self.total_time = 0  # 添加总用时记录

        # 初始化信号
        self.ui_signals = UIUpdateSignals()
        self.ui_signals.client_init_success.connect(self.onClientInitSuccess)
        self.ui_signals.client_init_failure.connect(self.onClientInitFailure)
        self.ui_signals.append_text.connect(self.appendFeedbackText)
        self.ui_signals.clear_text.connect(self.clearFeedbackText)

        self.setupUI()
        # self.initExercise()

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
        self.upper_container = QWidget()
        self.upper_container.setMinimumHeight(400)  # 设置最小高度
        upper_layout = QVBoxLayout(self.upper_container)
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

        # 下部分：点评区域
        self.feedback_container = QWidget()
        self.feedback_container.setMinimumHeight(150)  # 设置最小高度
        # self.feedback_container.setMaximumHeight(200)  # 设置最大高度限制
        feedback_layout = QVBoxLayout(self.feedback_container)

        # 为点评容器创建阴影效果
        feedback_shadow = QGraphicsDropShadowEffect(self)
        feedback_shadow.setBlurRadius(15)
        feedback_shadow.setXOffset(0)
        feedback_shadow.setYOffset(3)
        feedback_shadow.setColor(QColor(0, 0, 0, 30))
        self.feedback_container.setGraphicsEffect(feedback_shadow)

        # 点评标题栏
        feedback_header = QWidget()
        feedback_header_layout = QHBoxLayout(feedback_header)
        feedback_header_layout.setContentsMargins(0, 0, 0, 0)

        feedback_label = QLabel("AI点评")
        feedback_label.setStyleSheet("color: #666; font-weight: bold;")

        # 添加重试按钮
        self.retry_button = QPushButton("重新获取")
        self.retry_button.setEnabled(False)  # 初始状态禁用
        self.retry_button.setFixedSize(70, 24)
        self.retry_button.clicked.connect(self.retryFeedback)
        self.retry_button.setStyleSheet(
            """
            QPushButton {
                background: #9C27B0;
                color: white;
                border: none;
                border-radius: 3px;
                margin-left: 5px;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
            QPushButton:pressed {
                background: #6A1B9A;
            }
            QPushButton:disabled {
                background: #BDBDBD;
            }
        """
        )

        # 添加AI点评开关
        self.ai_toggle = QPushButton("启用AI点评")
        self.ai_toggle.setCheckable(True)  # 使按钮可切换
        self.ai_toggle.setFixedSize(90, 24)
        self.ai_toggle.setStyleSheet(
            """
            QPushButton {
                background: #e0e0e0;
                color: #666;
                border: none;
                border-radius: 12px;
                padding: 0 10px;
                text-align: center;
            }
            QPushButton:checked {
                background: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background: #BDBDBD;
            }
            QPushButton:checked:hover {
                background: #45a049;
            }
            QPushButton:disabled {
                background: #e0e0e0;
            }
        """
        )
        self.ai_toggle.toggled.connect(self.onAIToggled)

        # 添加设置按钮
        self.settings_button = QPushButton("设置")
        self.settings_button.setEnabled(False)
        self.settings_button.setFixedSize(50, 24)
        self.settings_button.clicked.connect(self.showSettingsDialog)
        self.settings_button.setStyleSheet(
            """
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #1976D2;
            }
            QPushButton:pressed {
                background: #1565C0;
            }
            QPushButton:disabled {
                background: #BDBDBD;
            }
        """
        )

        # 修改预览按钮样式
        self.preview_button = QPushButton("预览")
        self.preview_button.setEnabled(False)
        self.preview_button.setFixedSize(50, 24)
        self.preview_button.clicked.connect(self.showPreview)
        self.preview_button.setStyleSheet(
            """
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #F57C00;
            }
            QPushButton:pressed {
                background: #EF6C00;
            }
            QPushButton:disabled {
                background: #BDBDBD;
            }
        """
        )

        feedback_header_layout.addWidget(feedback_label)
        feedback_header_layout.addWidget(self.retry_button)
        feedback_header_layout.addStretch()
        feedback_header_layout.addWidget(self.ai_toggle)
        feedback_header_layout.addWidget(self.settings_button)
        feedback_header_layout.addWidget(self.preview_button)

        # 点评文本区域
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setStyleSheet(
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

        feedback_layout.addWidget(feedback_header)
        feedback_layout.addWidget(self.feedback_text)

        # 将上下部分添加到分割器
        self.splitter.addWidget(self.upper_container)
        self.splitter.addWidget(self.feedback_container)

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
        card = QuestionCard(question_text)
        # 使用固定值捕获当前索引
        card.submit_button.clicked.connect(self.handleAnswer)
        card.answer_input.returnPressed.connect(self.handleAnswer)

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

    def handleAnswer(self):
        print(f"question_index: {self.current_question_index}")
        if self.current_question_index >= len(self.question_cards):
            return

        card = self.question_cards[self.current_question_index]
        list_item = self.question_list.item(self.current_question_index)

        try:
            answer = float(card.answer_input.text())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字！")
            return

        # 计算本题耗时
        current_time = time.time()
        time_spent = int(current_time - self.exercise.last_answer_time)
        # 更新最后答题时间
        self.exercise.last_answer_time = current_time

        # 更新总用时
        self.total_time = int(time.time() - self.start_time)

        # 提交答案并显示结果
        is_correct = self.exercise.submit_answer(self.current_question_index, answer, time_spent)

        card.showResult(is_correct, self.exercise.questions[self.current_question_index].answer)
        list_item.updateDisplay("正确" if is_correct else "错误")

        # 更新进度
        progress = (self.current_question_index + 1) / len(self.exercise.questions) * 100
        self.progress_bar.setValue(progress)

        # 记录答题信息
        question_record = QuestionRecord(
            content=self.exercise.questions[self.current_question_index].content,
            user_answer=answer,
            correct_answer=self.exercise.questions[self.current_question_index].answer,
            is_correct=is_correct,
            time_spent=time_spent,
        )
        self.exercise_record.add_question_record(question_record)

        # 更新当前题目索引并处理下一题
        self.current_question_index += 1

        # 如果还有下一题，添加新卡片
        if self.current_question_index < len(self.exercise.questions):
            self.addQuestionCard(self.exercise.questions[self.current_question_index].content)
            next_list_item = self.question_list.item(self.current_question_index)
            next_list_item.updateDisplay("当前")
            self.question_list.setCurrentItem(next_list_item)
        else:
            # 练习完成
            final_score = self.exercise.submit_exercise()
            self.exercise_record.total_time = self.total_time
            self.exercise_record.final_score = final_score

            completion_msg = (
                f"练习已完成！\n"
                f"最终得分：{final_score}分\n"
                f"用时：{self.formatTime(self.total_time)}"
            )

            # 如果启用了AI点评
            if self.ai_toggle.isChecked() and self.poe_client is not None:
                completion_msg += "\n\n正在生成AI点评..."
                self.upper_container.setMinimumHeight(0)  # 取消最小高度

            QMessageBox.information(self, "练习完成", completion_msg)

            # 仅在启用AI点评且客户端存在时获取反馈
            if self.ai_toggle.isChecked() and self.poe_client is not None:
                self.getFeedback()

    def onClientInitSuccess(self, client):
        """客户端初始化成功的处理"""
        self.poe_client = client
        self.feedback_text.append("AI点评客户端初始化成功！")
        self.settings_button.setEnabled(True)
        self.ai_toggle.setEnabled(True)

    def onClientInitFailure(self, error_msg):
        """客户端初始化失败的处理"""
        self.feedback_text.append(f"初始化失败：{error_msg}")
        self.settings_button.setEnabled(True)
        self.ai_toggle.setEnabled(True)
        self.disableAI()
        self.ai_toggle.setChecked(False)

    def appendFeedbackText(self, text: str):
        """在主线程中添加反馈文本"""
        cursor = self.feedback_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.feedback_text.setTextCursor(cursor)

    def clearFeedbackText(self):
        """清除反馈文本"""
        self.feedback_text.clear()

    def onAIToggled(self, checked: bool):
        """处理AI点评开关状态改变"""
        if self.ignore_ai_toggle:  # 如果标志为True，不执行切换操作
            return

        self.settings_button.setEnabled(checked)
        if not checked:
            self.disableAI()
        else:
            self.ai_toggle.setText("关闭AI点评")
            self.ui_signals.clear_text.emit()
            self.feedback_text.setPlaceholderText(
                "AI点评功能已启用，请先在设置中配置token"
            )

    def disableAI(self):
        """禁用AI相关功能"""
        self.poe_client = None
        self.ai_toggle.setText("启用AI点评")
        self.feedback_text.clear()
        self.feedback_text.setPlaceholderText("")
        self.preview_button.setEnabled(False)

    def showSettingsDialog(self):
        """显示设置对话框"""
        dialog = AISettingsDialog(self)
        if dialog.exec():
            # 获取输入的token
            pb = dialog.pb_input.text()
            plat = dialog.plat_input.text()

            # 清空反馈文本并显示初始化消息
            self.ui_signals.clear_text.emit()
            self.ui_signals.append_text.emit("正在初始化AI点评客户端...")

            # 禁用相关按钮
            self.settings_button.setEnabled(False)
            self.ai_toggle.setEnabled(False)

            # 在子线程中初始化客户端
            def init_client():
                try:
                    tokens = {
                        "p-b": pb,
                        "p-lat": plat,
                    }

                    client = PoeApi(tokens=tokens, auto_proxy=True)
                    self.ui_signals.client_init_success.emit(client)

                except Exception as e:
                    self.ui_signals.client_init_failure.emit(str(e))

            # 启动初始化线程
            Thread(target=init_client, daemon=True).start()

    def showPreview(self):
        """显示预览窗口"""
        text = self.feedback_text.toPlainText()
        if text:
            if self.preview_window is None:
                self.preview_window = PreviewWindow(text)
            else:
                self.preview_window.close()
                self.preview_window = PreviewWindow(text)
            self.preview_window.show()

    def getFeedback(self):
        """获取AI反馈"""
        self.ui_signals.clear_text.emit()
        self.ui_signals.append_text.emit("正在生成评语，请稍候...")
        self.settings_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        self.retry_button.setEnabled(True)  # 激活重试按钮

        # 禁用AI开关按钮
        self.ignore_ai_toggle = True
        self.ai_toggle.setEnabled(False)

        # 重置停止事件
        self.stop_event.clear()

        def send_message():
            try:
                message = self.exercise_record.to_prompt_message()
                first_chunk = True

                # 流式输出AI回复
                for chunk in self.poe_client.send_message("chinchilla", message):
                    # 检查是否需要停止
                    if self.stop_event.is_set():
                        return

                    if first_chunk:
                        self.ui_signals.clear_text.emit()
                        first_chunk = False
                    self.ui_signals.append_text.emit(chunk["response"])

                # 在主线程中启用相关按钮
                def enable_buttons():
                    self.settings_button.setEnabled(True)
                    self.preview_button.setEnabled(True)
                    self.ai_toggle.setEnabled(True)
                    self.retry_button.setEnabled(False)  # 完成后禁用重试按钮
                    self.ignore_ai_toggle = False

                QApplication.instance().postEvent(
                    self, QEvent(QEvent.Type(QEvent.User + 1))
                )
                enable_buttons()

            except Exception as e:

                def handle_error():
                    self.ui_signals.clear_text.emit()
                    self.ui_signals.append_text.emit(f"\n获取AI反馈失败：{str(e)}")
                    self.settings_button.setEnabled(True)
                    self.preview_button.setEnabled(False)
                    self.ai_toggle.setEnabled(True)
                    self.retry_button.setEnabled(True)  # 失败时保持重试按钮激活
                    self.ignore_ai_toggle = False

                handle_error()

        # 保存线程引用
        self.feedback_thread = Thread(target=send_message, daemon=True)
        self.feedback_thread.start()

    def retryFeedback(self):
        """重试获取反馈"""
        if self.feedback_thread and self.feedback_thread.is_alive():
            # 设置停止标志
            self.stop_event.set()
            # 等待线程结束
            self.feedback_thread.join(timeout=1.0)

        # 重新获取反馈
        self.getFeedback()

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

        # 重置当前题目索引
        self.current_question_index = 0
        
        # 重置布局
        while self.questions_container.count():
            item = self.questions_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 初始化练习
        self.exercise = Exercise(
            difficulty=self.difficulty,
            number_range=self.number_range,
            operators=self.operators,
        )
        self.exercise.add_observer(Student("测试用户"))
        self.exercise.set_scoring_strategy(self.scoring_strategy)

        # 初始化练习记录
        self.exercise_record = ExerciseRecord(
            difficulty=DifficultyLevel.EASY.value,
            number_range=(-100, 100),
            operator_types=["加法", "减法", "乘法", "除法"],
        )

        # 生成题目
        self.exercise.generate_questions(self.question_count)

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
        self.initExercise()
