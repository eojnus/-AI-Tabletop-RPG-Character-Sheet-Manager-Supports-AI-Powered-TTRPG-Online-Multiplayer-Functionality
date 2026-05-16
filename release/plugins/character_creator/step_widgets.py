"""
分步引导界面 — 每个步骤对应一个 QWidget
"""
import json
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QTextEdit, QGridLayout, QGroupBox,
    QScrollArea, QListWidget, QListWidgetItem, QMessageBox,
    QCheckBox, QLineEdit, QAbstractItemView,
)
from PySide6.QtCore import Qt

from .dice_roller import roll_coc_attributes, roll_dnd_attributes
from .coc_data import (
    OCCUPATIONS, get_occupations, get_occupation_skills,
    calc_occupation_skill_points, calc_personal_skill_points,
    SKILL_BASE_VALUES,
)
from .dnd_data import (
    RACES, CLASSES, BACKGROUNDS,
    get_races, get_classes, get_backgrounds,
    get_skill_options_for_class,
)


# ==================== Step 1: 选择游戏模式 ====================

from PySide6.QtCore import Signal


class StepGameMode(QWidget):
    """第一步: 选择要创建角色的游戏"""

    mode_selected = Signal(str)  # 发射 "coc" 或 "dnd"

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🎮 选择游戏模式")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("请选择你要创建的角色卡类型：")
        desc.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.6);")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)

        self._coc_btn = QPushButton("🎭 克苏鲁的呼唤\nCOC 7th")
        self._coc_btn.setMinimumSize(200, 120)
        self._coc_btn.setStyleSheet("""
            QPushButton {
                background: rgba(108,99,255,0.15);
                border: 2px solid rgba(108,99,255,0.3);
                border-radius: 16px;
                font-size: 16px;
                padding: 20px;
            }
            QPushButton:hover { background: rgba(108,99,255,0.25); }
        """)
        self._coc_btn.setCheckable(True)
        self._dnd_btn = QPushButton("🐉 龙与地下城\nDND 5e")
        self._dnd_btn.setMinimumSize(200, 120)
        self._dnd_btn.setStyleSheet("""
            QPushButton {
                background: rgba(61,214,140,0.15);
                border: 2px solid rgba(61,214,140,0.3);
                border-radius: 16px;
                font-size: 16px;
                padding: 20px;
            }
            QPushButton:hover { background: rgba(61,214,140,0.25); }
        """)
        self._dnd_btn.setCheckable(True)

        self._coc_btn.toggled.connect(lambda c: self._on_mode_toggled("coc", c))
        self._dnd_btn.toggled.connect(lambda c: self._on_mode_toggled("dnd", c))

        btn_layout.addStretch()
        btn_layout.addWidget(self._coc_btn)
        btn_layout.addWidget(self._dnd_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        layout.addStretch()

    def _on_mode_toggled(self, mode, checked):
        if checked:
            self.mode_selected.emit(mode)
            # 取消另一个按钮的选中
            if mode == "coc":
                self._dnd_btn.setChecked(False)
            else:
                self._coc_btn.setChecked(False)

    def get_mode(self):
        if self._coc_btn.isChecked():
            return "coc"
        elif self._dnd_btn.isChecked():
            return "dnd"
        return None


# ==================== Step 2: 选择职业/种族 ====================

class StepChooseClass(QWidget):
    """第二步: COC选职业 / DND选种族+职业+背景"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "coc"
        self._setup_ui()

    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(12)

        self._title = QLabel("📋 选择职业")
        self._title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self._layout.addWidget(self._title)

        # 用一个 stacked widget 切换 COC/DND 的不同选择界面
        self._stack = QWidget()
        self._stack_layout = QVBoxLayout(self._stack)
        self._stack_layout.setContentsMargins(0, 0, 0, 0)

        # --- COC 选择 ---
        self._coc_widget = QWidget()
        coc_layout = QVBoxLayout(self._coc_widget)
        coc_layout.setSpacing(8)

        coc_layout.addWidget(QLabel("选择你的职业："))
        self._coc_occ_list = QListWidget()
        for occ in get_occupations():
            item = QListWidgetItem(occ)
            self._coc_occ_list.addItem(item)
        coc_layout.addWidget(self._coc_occ_list)

        self._coc_preview = QTextEdit()
        self._coc_preview.setReadOnly(True)
        self._coc_preview.setMaximumHeight(120)
        self._coc_preview.setPlaceholderText("选择职业后在此预览…")
        self._coc_occ_list.currentTextChanged.connect(self._preview_coc_occupation)
        coc_layout.addWidget(self._coc_preview)

        # --- DND 选择 ---
        self._dnd_widget = QWidget()
        dnd_layout = QVBoxLayout(self._dnd_widget)
        dnd_layout.setSpacing(8)

        form_grid = QGridLayout()
        form_grid.addWidget(QLabel("种族:"), 0, 0)
        self._dnd_race = QComboBox()
        self._dnd_race.addItems(get_races())
        self._dnd_race.currentTextChanged.connect(self._preview_dnd)
        form_grid.addWidget(self._dnd_race, 0, 1)

        form_grid.addWidget(QLabel("职业:"), 1, 0)
        self._dnd_class = QComboBox()
        self._dnd_class.addItems(get_classes())
        self._dnd_class.currentTextChanged.connect(self._preview_dnd)
        form_grid.addWidget(self._dnd_class, 1, 1)

        form_grid.addWidget(QLabel("背景:"), 2, 0)
        self._dnd_bg = QComboBox()
        self._dnd_bg.addItems(get_backgrounds())
        self._dnd_bg.currentTextChanged.connect(self._preview_dnd)
        form_grid.addWidget(self._dnd_bg, 2, 1)

        form_grid.addWidget(QLabel("等级:"), 3, 0)
        self._dnd_level = QSpinBox()
        self._dnd_level.setRange(1, 20)
        self._dnd_level.setValue(1)
        form_grid.addWidget(self._dnd_level, 3, 1)

        dnd_layout.addLayout(form_grid)

        self._dnd_preview = QTextEdit()
        self._dnd_preview.setReadOnly(True)
        self._dnd_preview.setMaximumHeight(150)
        dnd_layout.addWidget(self._dnd_preview)

        self._stack_layout.addWidget(self._coc_widget)
        self._stack_layout.addWidget(self._dnd_widget)
        self._coc_widget.show()
        self._dnd_widget.hide()

        self._layout.addWidget(self._stack)

    def set_mode(self, mode):
        self.mode = mode
        self._coc_widget.setVisible(mode == "coc")
        self._dnd_widget.setVisible(mode == "dnd")
        if mode == "coc":
            self._title.setText("📋 选择职业")
        else:
            self._title.setText("📋 选择种族、职业、背景")

    def _preview_coc_occupation(self, occ_name):
        if not occ_name:
            return
        occ = OCCUPATIONS.get(occ_name)
        if not occ:
            return
        skills = ", ".join(occ["skills"])
        cr = occ["credit_range"]
        text = (
            f"职业: {occ_name}\n"
            f"技能列表: {skills}\n"
            f"信用评级范围: {cr[0]}~{cr[1]}\n"
            f"职业技能点: EDU × {occ['skill_points_edu']}"
        )
        if occ["skill_points_other"] > 0:
            text += f" + {occ['other_stat']} × {occ['skill_points_other']}"
        self._coc_preview.setPlainText(text)

    def _preview_dnd(self):
        race = self._dnd_race.currentText()
        cls = self._dnd_class.currentText()
        bg = self._dnd_bg.currentText()
        lines = []
        if race:
            r = RACES.get(race)
            if r:
                bonus = ", ".join(f"{k}+{v}" for k, v in r["ability_bonus"].items() if v)
                lines.append(f"种族: {race} | 属性加值: {bonus}")
        if cls:
            c = CLASSES.get(cls)
            if c:
                lines.append(f"职业: {cls} | 生命骰: {c['hit_dice']} | 主属性: {c['primary_ability']}")
                skills = ", ".join(c["skill_options"])
                lines.append(f"可选技能(选{c['skill_choices']}): {skills}")
        if bg:
            b = BACKGROUNDS.get(bg)
            if b:
                skills = ", ".join(b["skill_proficiencies"])
                lines.append(f"背景: {bg} | 熟练技能: {skills}")
        self._dnd_preview.setPlainText("\n".join(lines))

    def get_selection(self):
        if self.mode == "coc":
            occ = self._coc_occ_list.currentItem()
            return {"occupation": occ.text() if occ else ""}
        else:
            return {
                "race": self._dnd_race.currentText(),
                "class": self._dnd_class.currentText(),
                "background": self._dnd_bg.currentText(),
                "level": self._dnd_level.value(),
            }

    def validate(self):
        """检查是否已选择"""
        if self.mode == "coc":
            return self._coc_occ_list.currentItem() is not None
        else:
            return True  # 默认都有值


# ==================== Step 3: 属性生成 ====================

class StepAttributes(QWidget):
    """第三步: 选择生成方式并产生属性"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "coc"
        self.attribute_values = {}
        self.roll_details = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self._title = QLabel("🎲 生成属性")
        self._title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self._title)

        # 生成方式选择
        method_row = QHBoxLayout()
        method_row.addWidget(QLabel("生成方式:"))
        self._method_combo = QComboBox()
        self._method_combo.currentTextChanged.connect(self._on_method_change)
        method_row.addWidget(self._method_combo, stretch=1)
        layout.addLayout(method_row)

        # 掷骰按钮
        self._roll_btn = QPushButton("🎲 掷骰生成")
        self._roll_btn.setObjectName("actionButton")
        self._roll_btn.clicked.connect(self._roll_attributes)
        layout.addWidget(self._roll_btn)

        # 属性结果显示
        self._attr_widgets = {}
        attr_grid = QGridLayout()
        self._attr_names_coc = ["力量", "体质", "意志", "敏捷", "外貌", "体型", "智力", "教育"]
        self._attr_names_dnd = ["力量", "敏捷", "体质", "智力", "感知", "魅力"]

        for i, name in enumerate(self._attr_names_coc):
            row, col = i // 2, i % 2
            w = QSpinBox()
            w.setRange(1, 999)
            w.setMinimumWidth(80)
            w.setEnabled(False)
            self._attr_widgets[name] = w
            attr_grid.addWidget(QLabel(f"{name}:"), row, col * 2)
            attr_grid.addWidget(w, row, col * 2 + 1)

        # DND 购点法特殊控件
        self._point_buy_widget = QWidget()
        pb_layout = QVBoxLayout(self._point_buy_widget)
        pb_layout.setContentsMargins(0, 0, 0, 0)
        self._point_buy_label = QLabel("购点法: 剩余 27 点\n初始全部为 8")
        self._point_buy_label.setStyleSheet("color: rgba(255,255,255,0.7);")
        pb_layout.addWidget(self._point_buy_label)
        pb_grid = QGridLayout()
        self._pb_spins = {}
        for i, name in enumerate(self._attr_names_dnd):
            w = QSpinBox()
            w.setRange(8, 15)
            w.setValue(8)
            w.valueChanged.connect(self._update_point_buy)
            self._pb_spins[name] = w
            pb_grid.addWidget(QLabel(name), i // 3, (i % 3) * 2)
            pb_grid.addWidget(w, i // 3, (i % 3) * 2 + 1)
        pb_layout.addLayout(pb_grid)
        self._point_buy_widget.hide()

        layout.addLayout(attr_grid)
        layout.addWidget(self._point_buy_widget)

        # 掷骰细节
        self._detail_text = QTextEdit()
        self._detail_text.setReadOnly(True)
        self._detail_text.setMaximumHeight(100)
        self._detail_text.setPlaceholderText("点击「掷骰生成」后显示每次掷骰的结果…")
        layout.addWidget(self._detail_text)

        layout.addStretch()

    def set_mode(self, mode):
        self.mode = mode
        self._method_combo.blockSignals(True)
        self._method_combo.clear()

        if mode == "coc":
            self._method_combo.addItems(["3d6×5（推荐）", "2d6+6×5（高属性）"])
            names = self._attr_names_coc
            self._point_buy_widget.hide()
        else:
            self._method_combo.addItems(["4d6去最低（推荐）", "标准属性数组", "购点法（27点）"])
            names = self._attr_names_dnd

        # 显示/隐藏对应的属性行
        for name in self._attr_names_coc + self._attr_names_dnd:
            if name in self._attr_widgets:
                w = self._attr_widgets[name]
                lbl = None
                # 找对应的 label
                w.setVisible(name in names)

        self._method_combo.blockSignals(False)
        self._on_method_change()

    def _on_method_change(self):
        method = self._method_combo.currentText()
        if self.mode == "dnd" and "购点" in method:
            self._point_buy_widget.show()
            self._roll_btn.hide()
        else:
            self._point_buy_widget.hide()
            self._roll_btn.show()

    def _update_point_buy(self):
        """购点法计算剩余点数"""
        cost_map = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
        total = 27
        used = sum(cost_map.get(w.value(), 0) for w in self._pb_spins.values())
        remaining = total - used
        self._point_buy_label.setText(f"购点法: 剩余 {remaining} 点  已用 {used} 点")
        self._point_buy_label.setStyleSheet(
            "color: red;" if remaining < 0 else "color: rgba(255,255,255,0.7);"
        )

    def _roll_attributes(self):
        method = self._method_combo.currentText()

        if self.mode == "coc":
            if "2d6+6" in method:
                results, details = roll_coc_attributes("2d6+6x5")
            else:
                results, details = roll_coc_attributes("3d6x5")
        else:
            if "标准" in method:
                results, details = roll_dnd_attributes("standard_array")
            else:
                results, details = roll_dnd_attributes("4d6")

        self.attribute_values = results

        # 更新显示
        for name, val in results.items():
            if name in self._attr_widgets:
                self._attr_widgets[name].setValue(val)

        # 细节文本
        lines = []
        for name, (rolls, val) in details.items():
            if rolls:
                lines.append(f"{name}: 掷出 {rolls} → {val}")
            else:
                name_cn = {"strength": "力量", "dexterity": "敏捷", "constitution": "体质",
                           "intelligence": "智力", "wisdom": "感知", "charisma": "魅力"}
                actual_name = name_cn.get(name, name)
                lines.append(f"{actual_name}: 固定值 {val}")
        self._detail_text.setPlainText("\n".join(lines))

    def get_attributes(self):
        """获取最终属性值"""
        method = self._method_combo.currentText()
        if self.mode == "dnd" and "购点" in method:
            return {name: w.value() for name, w in self._pb_spins.items()}
        return dict(self.attribute_values)

    def validate(self):
        method = self._method_combo.currentText()
        if self.mode == "dnd" and "购点" in method:
            cost_map = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
            total = sum(cost_map.get(w.value(), 0) for w in self._pb_spins.values())
            return total <= 27
        return bool(self.attribute_values) or ("购点" in method)


# ==================== Step 4: 分配技能 ====================

class StepSkills(QWidget):
    """第四步: 分配技能点数"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "coc"
        self.selection = {}
        self.attributes = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self._title = QLabel("📝 分配技能")
        self._title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self._title)

        self._info_label = QLabel("")
        self._info_label.setStyleSheet("color: rgba(255,255,255,0.6);")
        layout.addWidget(self._info_label)

        # 指示当前分配阶段
        self._phase_label = QLabel("")
        self._phase_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #6c63ff;")
        layout.addWidget(self._phase_label)

        # 技能列表（可滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self._skill_container = QWidget()
        self._skill_grid = QVBoxLayout(self._skill_container)
        scroll.setWidget(self._skill_container)
        layout.addWidget(scroll, stretch=1)

        # 点数余量
        self._remaining_label = QLabel("剩余点数: 0")
        self._remaining_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(self._remaining_label)

        # 切换阶段按钮
        phase_row = QHBoxLayout()
        self._next_phase_btn = QPushButton("下一步 → 分配个人技能")
        self._next_phase_btn.setObjectName("actionButton")
        self._next_phase_btn.clicked.connect(self._switch_to_personal)
        phase_row.addStretch()
        phase_row.addWidget(self._next_phase_btn)
        self._phase_btn_row = phase_row
        layout.addLayout(phase_row)

        self._skill_spins = {}  # name -> QSpinBox
        self._phase = "occupation"  # occupation / personal
        self._occupation_skills = []
        self._occ_max = 0
        self._personal_max = 0
        self._occ_used = 0
        self._personal_used = 0

    def set_data(self, mode, selection, attributes):
        self.mode = mode
        self.selection = selection
        self.attributes = attributes

        # 清空旧控件
        while self._skill_grid.count():
            item = self._skill_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._skill_spins.clear()

        if mode == "coc":
            self._setup_coc_skills()
        else:
            self._setup_dnd_skills()

    def _setup_coc_skills(self):
        occ_name = self.selection.get("occupation", "")
        occ = OCCUPATIONS.get(occ_name, {})
        self._occupation_skills = occ.get("skills", [])
        edu = self.attributes.get("教育", 50)
        int_val = self.attributes.get("智力", 50)
        self._occ_max = calc_occupation_skill_points(occ_name, type("obj", (), {"education": edu, "dexterity": 50})())
        self._personal_max = calc_personal_skill_points(type("obj", (), {"intelligence": int_val})())

        self._info_label.setText(
            f"职业技能点: {self._occ_max} | 个人兴趣点: {self._personal_max}"
        )
        self._phase = "occupation"
        self._phase_label.setText("▸ 阶段一: 分配职业技能")
        self._next_phase_btn.setText("下一步 → 分配个人兴趣技能")
        self._occ_used = 0
        self._personal_used = 0

        # 按职业技能/其他技能分组展示
        for skill_name, base_val in sorted(SKILL_BASE_VALUES.items()):
            if skill_name == "信用评级":
                continue  # 特殊处理
            row = QHBoxLayout()
            is_occ = skill_name in self._occupation_skills
            label_text = f"{skill_name} (基础 {base_val})"
            if is_occ:
                label_text += " 🔵"  # 标记为职业技能
            label = QLabel(label_text)
            label.setMinimumWidth(180)
            if is_occ:
                label.setStyleSheet("color: #6c63ff;")

            w = QSpinBox()
            w.setRange(base_val, 99)
            w.setValue(base_val)
            w.setFixedWidth(110)
            w.setStyleSheet("""
                QSpinBox {
                    background: rgba(255,255,255,0.08);
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 6px;
                    padding: 4px 16px 4px 8px;
                    color: white;
                    font-size: 13px;
                    min-width: 70px;
                }
                QSpinBox:focus {
                    border: 1px solid rgba(108,99,255,0.4);
                }
                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 24px;
                    border-left: 1px solid rgba(255,255,255,0.1);
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                    border-top-right-radius: 6px;
                    background: rgba(108,99,255,0.15);
                }
                QSpinBox::up-button:hover {
                    background: rgba(108,99,255,0.3);
                }
                QSpinBox::up-arrow {
                    width: 10px;
                    height: 10px;
                }
                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 24px;
                    border-left: 1px solid rgba(255,255,255,0.1);
                    border-bottom-right-radius: 6px;
                    background: rgba(108,99,255,0.15);
                }
                QSpinBox::down-button:hover {
                    background: rgba(108,99,255,0.3);
                }
                QSpinBox::down-arrow {
                    width: 10px;
                    height: 10px;
                }
            """)
            w.valueChanged.connect(self._update_remaining)
            self._skill_spins[skill_name] = w

            row.addWidget(label)
            row.addSpacing(8)
            row.addWidget(w)
            row.addStretch()
            self._skill_grid.addLayout(row)

        # 信用评级单独一行
        cr_row = QHBoxLayout()
        cr_range = occ.get("credit_range", (0, 30))
        cr_label = QLabel(f"信用评级 (范围: {cr_range[0]}~{cr_range[1]}) 🔵")
        cr_label.setStyleSheet("color: #6c63ff;")
        self._cr_spin = QSpinBox()
        self._cr_spin.setRange(cr_range[0], cr_range[1])
        self._cr_spin.setValue(cr_range[0])
        self._cr_spin.setFixedWidth(70)
        cr_row.addWidget(cr_label)
        cr_row.addWidget(self._cr_spin)
        cr_row.addStretch()
        self._skill_grid.addLayout(cr_row)

        self._update_remaining()

    def _setup_dnd_skills(self):
        self._phase = "skills"
        self._phase_label.setText("▸ 选择技能熟练项")
        self._next_phase_btn.hide()

        class_name = self.selection.get("class", "")
        cls = CLASSES.get(class_name, {})
        skill_opts = cls.get("skill_options", [])
        skill_count = cls.get("skill_choices", 2)

        # 背景技能
        bg_name = self.selection.get("background", "")
        bg = BACKGROUNDS.get(bg_name, {})
        bg_skills = bg.get("skill_proficiencies", [])

        self._info_label.setText(
            f"职业「{class_name}」可选 {skill_count} 项技能 | "
            f"背景「{bg_name}」固定技能: {', '.join(bg_skills)}"
        )

        # 技能列表
        dnd_skill_names = [
            "运动", "巧手", "隐匿", "奥秘", "历史", "调查",
            "自然", "宗教", "驯兽", "洞察", "医疗", "察觉",
            "生存", "欺瞒", "威吓", "表演", "游说",
        ]

        for skill_name in dnd_skill_names:
            row = QHBoxLayout()
            is_bg = skill_name in bg_skills
            label_text = skill_name
            if is_bg:
                label_text += " (背景熟练) 🟢"
                label = QLabel(label_text)
                label.setStyleSheet("color: #3dd68c;")
            else:
                label = QLabel(label_text)

            w = QSpinBox()
            w.setRange(0, 2)
            if is_bg:
                w.setValue(1)
                w.setEnabled(False)  # 背景技能固定熟练
            elif skill_name in skill_opts:
                w.setValue(0)
            else:
                w.setValue(0)
                w.setEnabled(False)  # 不可选
            w.setFixedWidth(60)
            self._skill_spins[skill_name] = w

            row.addWidget(label)
            row.addWidget(w)
            row.addStretch()
            self._skill_grid.addLayout(row)

        self._remaining_label.setText(f"总熟练项: 背景{len(bg_skills)} + 可选职业")
        self._remaining_label.hide()

    def _switch_to_personal(self):
        """切换到个人兴趣技能阶段"""
        if self._phase == "occupation":
            # 先更新数值
            self._update_remaining()
            # 检查职业技能点是否用完
            occ_remaining = self._occ_max - self._occ_used
            if occ_remaining > 0:
                QMessageBox.warning(
                    self, "提示",
                    f"还有 {occ_remaining} 点职业技能未分配！\n必须用完所有职业技能点才能进入下一步。"
                )
                return
            if occ_remaining < 0:
                QMessageBox.warning(
                    self, "提示",
                    f"职业技能超支了 {-occ_remaining} 点！请调整。"
                )
                return
            self._phase = "personal"
            self._phase_label.setText("▸ 阶段二: 分配个人兴趣技能")
            self._next_phase_btn.setText("✅ 技能分配完成")
            self._next_phase_btn.clicked.disconnect()
            self._next_phase_btn.clicked.connect(self._finish_skills)
            self._update_remaining()

    def _finish_skills(self):
        """技能分配完成 - 显示完成状态"""
        self._phase_label.setText("✅ 技能分配完成")
        self._next_phase_btn.hide()

    def _update_remaining(self):
        """更新剩余点数显示"""
        if self.mode == "coc":
            if self._phase == "occupation":
                # 计算职业技能已用
                used = sum(
                    w.value() - SKILL_BASE_VALUES.get(name, 0)
                    for name, w in self._skill_spins.items()
                    if name in self._occupation_skills
                )
                used += self._cr_spin.value()  # 信用评级
                occ_remaining = self._occ_max - used
                self._occ_used = used

                # 计算个人兴趣已用（只作展示）
                personal_used = sum(
                    w.value() - SKILL_BASE_VALUES.get(name, 0)
                    for name, w in self._skill_spins.items()
                    if name not in self._occupation_skills
                )
                personal_remaining = self._personal_max - personal_used
                self._personal_used = personal_used

                text = f"职业技能剩余: {max(0, occ_remaining)} / {self._occ_max} 点"
                text += f"  |  个人兴趣剩余: {max(0, personal_remaining)} / {self._personal_max} 点"
                if occ_remaining < 0:
                    text += " ⚠️ 职业技能超支了!"
                self._remaining_label.setText(text)
                self._remaining_label.setStyleSheet(
                    "color: red; font-size: 15px; font-weight: bold;"
                    if occ_remaining < 0 else
                    "color: white; font-size: 15px; font-weight: bold;"
                )
            else:
                # 个人技能（只显示个人兴趣点）
                used = sum(
                    w.value() - SKILL_BASE_VALUES.get(name, 0)
                    for name, w in self._skill_spins.items()
                    if name not in self._occupation_skills
                )
                remaining = self._personal_max - used
                self._personal_used = used
                self._remaining_label.setText(
                    f"个人兴趣剩余: {remaining} / {self._personal_max} 点"
                    + (" ✅ 分配完成" if remaining == 0 else "")
                    + (" ⚠️ 超支了!" if remaining < 0 else "")
                )
                self._remaining_label.setStyleSheet(
                    "color: red; font-size: 15px; font-weight: bold;"
                    if remaining < 0 else
                    "color: #3dd68c; font-size: 15px; font-weight: bold;"
                    if remaining == 0 else
                    "color: white; font-size: 15px; font-weight: bold;"
                )

    def get_skills(self):
        """获取所有技能值"""
        return {name: w.value() for name, w in self._skill_spins.items()}

    def validate(self):
        """检查点数是否合法"""
        if self.mode == "coc":
            self._update_remaining()
            # 职业技能必须用完且不超支
            if self._occ_used != self._occ_max:
                return False
            # 个人兴趣不能超支
            if self._personal_used > self._personal_max:
                return False
        return True


# ==================== Step 5: 装备 ====================

class StepEquipment(QWidget):
    """第五步: 初始装备"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "coc"
        self.selection = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self._title = QLabel("🎒 初始装备")
        self._title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self._title)

        self._default_label = QLabel("默认装备:")
        self._default_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._default_label)

        self._default_list = QTextEdit()
        self._default_list.setReadOnly(True)
        self._default_list.setMaximumHeight(100)
        layout.addWidget(self._default_list)

        self._extra_label = QLabel("额外物品（可选，每行一个）:")
        layout.addWidget(self._extra_label)

        self._extra_input = QTextEdit()
        self._extra_input.setPlaceholderText("手电筒\n打火机\n小刀\n备用弹药…")
        self._extra_input.setMaximumHeight(100)
        layout.addWidget(self._extra_input)

        layout.addStretch()

    def set_data(self, mode, selection):
        self.mode = mode
        self.selection = selection
        if mode == "coc":
            occ = selection.get("occupation", "")
            self._default_list.setPlainText(
                f"• {occ} 随身物品\n• 手机\n• 钱包/证件\n• 钥匙"
            )
        else:
            class_name = selection.get("class", "")
            cls = CLASSES.get(class_name, {})
            packages = cls.get("equipment_packages", [["基本冒险装备"]])
            items = "\n".join(f"• {item}" for item in packages[0])
            bg_name = selection.get("background", "")
            bg = BACKGROUNDS.get(bg_name, {})
            bg_items = "\n".join(f"• {item}" for item in bg.get("equipment", []))
            self._default_list.setPlainText(
                f"职业装备:\n{items}\n\n背景装备:\n{bg_items}"
            )

    def get_equipment(self):
        default = self._default_list.toPlainText()
        extra = self._extra_input.toPlainText()
        items = []
        for line in (default + "\n" + extra).split("\n"):
            line = line.strip().strip("•- ").strip()
            if line and line not in ["职业装备:", "背景装备:"]:
                items.append(line)
        return json.dumps(items, ensure_ascii=False)


# ==================== Step 6: 确认并创建 ====================

class StepConfirm(QWidget):
    """第六步: 确认角色信息并创建"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self._title = QLabel("✅ 确认创建")
        self._title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self._title)

        self._confirm_text = QTextEdit()
        self._confirm_text.setReadOnly(True)
        layout.addWidget(self._confirm_text, stretch=1)

    def set_summary(self, mode, name, selection, attributes, skills, equipment):
        lines = []
        lines.append(f"🎮 游戏: {'COC 7th' if mode == 'coc' else 'DND 5e'}")
        lines.append(f"📛 姓名: {name}")
        lines.append("")

        if mode == "coc":
            occ = selection.get("occupation", "")
            lines.append(f"💼 职业: {occ}")
            lines.append("")
            lines.append("📊 属性:")
            for k, v in attributes.items():
                lines.append(f"  {k}: {v}")
            lines.append("")
            lines.append("📋 技能:")
            for k, v in sorted(skills.items()):
                if v > 0:
                    lines.append(f"  {k}: {v}")
        else:
            lines.append(f"🔰 种族: {selection.get('race', '')}")
            lines.append(f"⚔️ 职业: {selection.get('class', '')} Lv.{selection.get('level', 1)}")
            lines.append(f"📖 背景: {selection.get('background', '')}")
            lines.append("")
            lines.append("📊 属性:")
            for k, v in attributes.items():
                lines.append(f"  {k}: {v}")

        lines.append("")
        lines.append("🎒 装备:")
        try:
            equip_list = json.loads(equipment)
            for item in equip_list:
                lines.append(f"  • {item}")
        except Exception:
            lines.append(f"  {equipment[:100]}")

        self._confirm_text.setPlainText("\n".join(lines))
