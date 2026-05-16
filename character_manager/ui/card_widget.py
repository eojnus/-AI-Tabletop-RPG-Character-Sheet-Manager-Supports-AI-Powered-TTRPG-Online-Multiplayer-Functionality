"""
单张角色卡组件 — 在九宫格中显示缩略信息
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class CardWidget(QFrame):
    """磨砂玻璃风格的单张角色卡片"""

    clicked = Signal(object)  # 发射角色对象

    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.setObjectName("cardWidget")
        self.character = character
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        # 获取摘要信息
        summary = self.character.get_card_summary()

        # 模式标签（COC / DND）
        mode_label = QLabel(summary.get("mode", ""))
        mode_label.setObjectName("modeIndicator")
        mode_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(mode_label)

        # 角色名
        name_label = QLabel(summary.get("name", "未命名"))
        name_label.setObjectName("titleLabel")
        name_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        name_label.setFont(font)
        layout.addWidget(name_label)

        # 副标题（职业/种族+职业）
        subtitle = QLabel(summary.get("subtitle", ""))
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # 分隔
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # 属性行
        for line_text in summary.get("lines", []):
            line = QLabel(line_text)
            line.setObjectName("statLabel")
            font = QFont()
            font.setPointSize(10)
            line.setFont(font)
            layout.addWidget(line)

        layout.addStretch()

    def mousePressEvent(self, event):
        """点击卡片时发射角色对象"""
        self.clicked.emit(self.character)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """鼠标进入时缩放效果"""
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开时恢复"""
        super().leaveEvent(event)
