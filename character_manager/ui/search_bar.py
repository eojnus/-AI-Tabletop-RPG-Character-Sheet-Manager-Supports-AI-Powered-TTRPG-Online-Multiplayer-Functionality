"""
搜索筛选栏组件 — 关键词搜索 + 多维度筛选 + 排序
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel,
)
from PySide6.QtCore import Signal


class SearchBar(QWidget):
    """搜索、筛选、排序一体化控制栏"""

    search_changed = Signal()  # 搜索条件变化时发射

    def __init__(self, mode="coc", parent=None):
        super().__init__(parent)
        self.mode = mode
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 8)
        layout.setSpacing(10)

        # 搜索框
        self._search_input = QLineEdit()
        self._search_input.setObjectName("searchBar")
        self._search_input.setPlaceholderText("🔍 搜索角色姓名或职业…")
        self._search_input.setMinimumWidth(200)
        self._search_input.textChanged.connect(self._on_change)
        layout.addWidget(self._search_input)

        # 性别筛选
        self._gender_filter = QComboBox()
        self._gender_filter.addItems(["全部性别", "男", "女", "其他"])
        self._gender_filter.currentTextChanged.connect(self._on_change)
        layout.addWidget(self._gender_filter)

        # 年龄筛选
        self._age_filter = QComboBox()
        self._age_filter.addItems(["全部年龄", "1-12岁", "13-17岁", "18-30岁", "31-50岁", "50岁以上"])
        self._age_filter.currentTextChanged.connect(self._on_change)
        layout.addWidget(self._age_filter)

        # 排序
        layout.addWidget(QLabel("排序:"))

        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["最近更新", "姓名", "年龄", "力量"])
        self._sort_combo.currentTextChanged.connect(self._on_change)
        layout.addWidget(self._sort_combo)

        # 排序方向
        self._sort_order_btn = QPushButton("↓ 降序")
        self._sort_order_btn.setObjectName("sortButton")
        self._sort_order_btn.setCheckable(True)
        self._sort_order_btn.clicked.connect(self._toggle_sort_order)
        layout.addWidget(self._sort_order_btn)

        layout.addStretch()

    def _on_change(self):
        """搜索条件变化"""
        self.search_changed.emit()

    def _toggle_sort_order(self):
        """切换升降序"""
        if self._sort_order_btn.isChecked():
            self._sort_order_btn.setText("↑ 升序")
        else:
            self._sort_order_btn.setText("↓ 降序")
        self.search_changed.emit()

    def get_search_params(self):
        """获取当前搜索参数"""
        # 年龄筛选
        age_map = {
            "全部年龄": (None, None),
            "1-12岁": (1, 12),
            "13-17岁": (13, 17),
            "18-30岁": (18, 30),
            "31-50岁": (31, 50),
            "50岁以上": (51, 999),
        }
        age_range = age_map.get(self._age_filter.currentText(), (None, None))

        # 排序字段
        sort_map = {
            "最近更新": "updated_at",
            "姓名": "name",
            "年龄": "age",
            "力量": "strength",
        }
        sort_by = sort_map.get(self._sort_combo.currentText(), "updated_at")
        sort_order = "ASC" if self._sort_order_btn.isChecked() else "DESC"

        # 性别
        gender_text = self._gender_filter.currentText()
        gender = None if gender_text == "全部性别" else gender_text

        return {
            "keyword": self._search_input.text().strip(),
            "filters": {
                "gender": gender,
                "age_min": age_range[0],
                "age_max": age_range[1],
            },
            "sort_by": sort_by,
            "sort_order": sort_order,
        }

    def set_mode(self, mode):
        """切换模式时更新筛选选项"""
        self.mode = mode
        if mode == "dnd":
            self._search_input.setPlaceholderText("🔍 搜索角色姓名、种族或职业…")
        else:
            self._search_input.setPlaceholderText("🔍 搜索角色姓名或职业…")
