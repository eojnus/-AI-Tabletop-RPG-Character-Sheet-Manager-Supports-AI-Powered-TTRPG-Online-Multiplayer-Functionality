"""
卡片网格组件 — 九宫格展示角色卡片
"""
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QVBoxLayout, QLabel,
)
from PySide6.QtCore import Qt, Signal
from .card_widget import CardWidget


class CardGrid(QScrollArea):
    """可滚动的卡片网格视图"""

    card_clicked = Signal(object)  # 发射角色对象

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardGridArea")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 内容容器
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self.setWidget(self._container)

        self._grid = QGridLayout(self._container)
        self._grid.setContentsMargins(20, 20, 20, 20)
        self._grid.setSpacing(16)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # 空状态提示
        self._empty_label = QLabel("✨ 还没有角色卡\n点击右上角 「📥 导入」添加你的第一个角色吧！")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet("""
            color: rgba(255,255,255,0.3);
            font-size: 16px;
            padding: 60px;
        """)
        self._grid.addWidget(self._empty_label, 0, 0, 1, 3)

        self._cards = []  # 当前展示的卡片列表

    def display_characters(self, characters):
        """展示角色列表（每次会清空重建）"""
        self._clear_grid()
        self._cards = []

        if not characters:
            self._grid.addWidget(self._empty_label, 0, 0, 1, 3)
            return

        row, col = 0, 0
        max_cols = 3  # 每行3列

        for character in characters:
            card = CardWidget(character)
            card.clicked.connect(self._on_card_clicked)
            self._grid.addWidget(card, row, col)
            self._cards.append(card)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # 在最后一行剩余位置填充空白以保持左对齐
        if col > 0:
            spacer = QWidget()
            spacer.setStyleSheet("background: transparent;")
            self._grid.addWidget(spacer, row, col, 1, max_cols - col)

    def _clear_grid(self):
        """清空网格"""
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_card_clicked(self, character):
        """卡片被点击"""
        self.card_clicked.emit(character)
