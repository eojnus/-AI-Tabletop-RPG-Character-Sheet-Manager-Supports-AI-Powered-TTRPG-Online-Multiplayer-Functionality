"""
角色详情查看/编辑窗口
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QFormLayout, QLineEdit,
    QSpinBox, QTextEdit, QScrollArea, QGroupBox, QGridLayout,
    QMessageBox, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import json

from ..models.coc_character import COCCharacter, COC_SKILL_DEFAULTS
from ..models.dnd_character import DNDCharacter, DND_SKILL_NAMES


class DetailDialog(QDialog):
    """角色详情对话框（查看+编辑）"""

    character_saved = Signal(object)   # 保存时发射
    character_deleted = Signal(object) # 删除时发射

    def __init__(self, character, mode, repository, parent=None):
        super().__init__(parent)
        self.setObjectName("detailWindow")
        self.character = character
        self.mode = mode
        self.repo = repository
        self._modified = False

        self.setWindowTitle(f"角色详情 — {character.name}")
        self.setMinimumSize(720, 560)
        self.setModal(True)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 标签页
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                background: rgba(0, 0, 0, 0.2);
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QTabBar::tab {
                background: transparent;
                color: rgba(255,255,255,0.5);
                border: none;
                padding: 8px 20px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                color: white;
                border-bottom: 2px solid #6c63ff;
            }
            QTabBar::tab:hover {
                color: rgba(255,255,255,0.8);
            }
        """)

        if self.mode == "coc":
            self._tabs.addTab(self._create_basic_tab(), "基本信息")
            self._tabs.addTab(self._create_coc_stats_tab(), "属性与技能")
            self._tabs.addTab(self._create_background_tab(), "背景与装备")
        else:
            self._tabs.addTab(self._create_basic_tab(), "基本信息")
            self._tabs.addTab(self._create_dnd_stats_tab(), "属性与技能")
            self._tabs.addTab(self._create_dnd_combat_tab(), "战斗与法术")
            self._tabs.addTab(self._create_background_tab(), "背景与装备")

        main_layout.addWidget(self._tabs)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 8, 20, 16)

        delete_btn = QPushButton("🗑️ 删除角色")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self._delete_character)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("sortButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 保存")
        save_btn.setObjectName("actionButton")
        save_btn.clicked.connect(self._save_character)
        btn_layout.addWidget(save_btn)

        main_layout.addLayout(btn_layout)

    def _create_basic_tab(self):
        """基本信息标签页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        form = QFormLayout(container)
        form.setSpacing(12)
        form.setContentsMargins(20, 16, 20, 16)

        self._basic_widgets = {}

        fields = [
            ("name", "姓名"), ("player_name", "玩家名"),
            ("age", "年龄"), ("gender", "性别"),
        ]
        if self.mode == "coc":
            fields.append(("occupation", "职业"))
        else:
            fields.extend([
                ("race", "种族"), ("class_name", "职业"),
                ("level", "等级"), ("background", "背景"),
                ("alignment", "阵营"),
            ])

        for key, label in fields:
            widget = QLineEdit()
            widget.setStyleSheet("""
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
            """)
            widget.textChanged.connect(self._mark_modified)
            self._basic_widgets[key] = widget
            form.addRow(QLabel(label + ":"), widget)

        # 时间信息
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel(f"创建: {self.character.created_at}"))
        time_layout.addWidget(QLabel(f"更新: {self.character.updated_at}"))
        form.addRow(time_layout)

        scroll.setWidget(container)
        return scroll

    def _create_coc_stats_tab(self):
        """COC 属性与技能标签页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(12)

        # 七项属性
        stat_group = QGroupBox("七项属性")
        stat_grid = QGridLayout(stat_group)
        self._stat_widgets = {}

        attr_names = [
            ("strength", "STR 力量"), ("constitution", "CON 体质"),
            ("power", "POW 意志"), ("dexterity", "DEX 敏捷"),
            ("appearance", "APP 外貌"), ("size", "SIZ 体型"),
            ("intelligence", "INT 智力"), ("education", "EDU 教育"),
        ]
        for i, (key, label) in enumerate(attr_names):
            row, col = i // 4, i % 4
            w = QSpinBox()
            w.setRange(1, 999)
            w.setStyleSheet("""
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 4px 8px;
                color: white;
            """)
            w.valueChanged.connect(self._mark_modified)
            self._stat_widgets[key] = w
            stat_grid.addWidget(QLabel(label), row * 2, col)
            stat_grid.addWidget(w, row * 2 + 1, col)

        layout.addWidget(stat_group)

        # 衍生属性（只读显示）
        derived_group = QGroupBox("衍生属性")
        derived_layout = QHBoxLayout(derived_group)
        self._derived_labels = {}
        for key, label in [("hp", "HP"), ("mp", "MP"), ("san", "SAN"),
                           ("luck", "幸运"), ("build", "Build"), ("dodge", "闪避"), ("move", "Move")]:
            lbl = QLabel(f"{label}: 0")
            lbl.setObjectName("statLabel")
            self._derived_labels[key] = lbl
            derived_layout.addWidget(lbl)
        layout.addWidget(derived_group)

        # 技能
        skill_group = QGroupBox("技能 (点击数值可编辑)")
        skill_scroll = QScrollArea()
        skill_scroll.setWidgetResizable(True)
        skill_scroll.setStyleSheet("background: transparent; border: none;")
        skill_container = QWidget()
        # 改为2列布局，给技能名和数值更多空间
        skill_grid = QGridLayout(skill_container)
        skill_grid.setSpacing(4)
        skill_grid.setContentsMargins(8, 4, 8, 4)

        self._skill_widgets = {}
        sorted_skills = sorted(COC_SKILL_DEFAULTS.keys())
        for i, skill_name in enumerate(sorted_skills):
            row, col = i // 2, i % 2
            lbl = QLabel(skill_name + ":")
            lbl.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; min-width: 80px;")
            w = QSpinBox()
            w.setRange(0, 999)
            w.setFixedWidth(70)
            w.setStyleSheet("""
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 2px 6px;
                color: white;
                font-size: 13px;
            """)
            w.valueChanged.connect(self._mark_modified)
            self._skill_widgets[skill_name] = w
            skill_grid.addWidget(lbl, row, col * 2)
            skill_grid.addWidget(w, row, col * 2 + 1)

        skill_scroll.setWidget(skill_container)
        skill_group.setLayout(QVBoxLayout())
        skill_group.layout().addWidget(skill_scroll)
        layout.addWidget(skill_group, stretch=1)

        scroll.setWidget(container)
        return scroll

    def _create_dnd_stats_tab(self):
        """DND 属性与技能标签页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)

        # 六项属性
        stat_group = QGroupBox("六项属性")
        stat_grid = QGridLayout(stat_group)
        self._stat_widgets = {}

        attr_names = [
            ("strength", "STR 力量"), ("dexterity", "DEX 敏捷"),
            ("constitution", "CON 体质"), ("intelligence", "INT 智力"),
            ("wisdom", "WIS 感知"), ("charisma", "CHA 魅力"),
        ]
        for i, (key, label) in enumerate(attr_names):
            row, col = i // 3, i % 3
            w = QSpinBox()
            w.setRange(1, 30)
            w.setStyleSheet("""
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 4px 8px;
                color: white;
            """)
            w.valueChanged.connect(self._mark_modified)
            self._stat_widgets[key] = w
            mod_label = QLabel("(+0)")
            mod_label.setObjectName("statLabel")
            stat_grid.addWidget(QLabel(label), row * 2, col)
            stat_grid.addWidget(w, row * 2 + 1, col)
            stat_grid.addWidget(mod_label, row * 2 + 1, col + 1)

        layout.addWidget(stat_group)

        # 技能
        skill_group = QGroupBox("技能熟练")
        skill_layout = QGridLayout(skill_group)
        self._skill_widgets = {}

        for i, skill_name in enumerate(DND_SKILL_NAMES):
            row, col = i // 3, i % 3
            w = QSpinBox()
            w.setRange(0, 2)
            w.setStyleSheet("""
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 4px;
                padding: 2px 6px;
                color: white;
                min-width: 50px;
            """)
            w.valueChanged.connect(self._mark_modified)
            self._skill_widgets[skill_name] = w
            skill_layout.addWidget(QLabel(skill_name + ":"), row, col * 2)
            skill_layout.addWidget(w, row, col * 2 + 1)

        layout.addWidget(skill_group)

        scroll.setWidget(container)
        return scroll

    def _create_dnd_combat_tab(self):
        """DND 战斗与法术标签页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        form = QFormLayout(container)
        form.setSpacing(12)

        self._combat_widgets = {}
        combat_fields = [
            ("hp_max", "最大HP"), ("hp_current", "当前HP"),
            ("temporary_hp", "临时HP"), ("armor_class", "护甲等级 (AC)"),
            ("initiative", "先攻加值"), ("speed", "速度"),
            ("proficiency_bonus", "熟练加值"), ("hit_dice", "生命骰 (如 d10)"),
        ]
        for key, label in combat_fields:
            if key == "hit_dice":
                w = QLineEdit()
            else:
                w = QSpinBox()
                w.setRange(-99, 9999)
            w.setStyleSheet("""
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
            """)
            w.valueChanged.connect(self._mark_modified) if hasattr(w, 'valueChanged') else None
            self._combat_widgets[key] = w
            form.addRow(QLabel(label + ":"), w)

        # 法术
        spells_group = QGroupBox("法术 (JSON格式)")
        spells_layout = QVBoxLayout(spells_group)
        self._spells_edit = QTextEdit()
        self._spells_edit.setStyleSheet("""
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 8px;
            color: white;
            font-family: 'Consolas', monospace;
        """)
        spells_layout.addWidget(self._spells_edit)
        form.addRow(spells_group)

        scroll.setWidget(container)
        return scroll

    def _create_background_tab(self):
        """背景与装备标签页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        form = QFormLayout(container)
        form.setSpacing(10)

        self._bg_widgets = {}

        if self.mode == "coc":
            bg_fields = [
                ("personal_description", "个人描述"),
                ("ideology_beliefs", "信念与意识形态"),
                ("significant_people", "重要之人"),
                ("meaningful_locations", "意义非凡之地"),
                ("treasured_possessions", "宝贵之物"),
                ("traits", "特质"),
                ("injuries_scars", "伤疤与伤痕"),
                ("phobias_manias", "恐惧与狂热"),
                ("arcane_tomes", "神秘典籍"),
                ("spells_and_artifacts", "法术与神器"),
                ("encounters_with_strange_entities", "异界遭遇"),
            ]
        else:
            bg_fields = [
                ("personality_traits", "个性特点"),
                ("ideals", "理念"),
                ("bonds", "羁绊"),
                ("flaws", "缺陷"),
                ("backstory", "背景故事"),
            ]

        for key, label in bg_fields:
            w = QTextEdit()
            w.setMaximumHeight(100)
            w.setStyleSheet("""
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 8px;
                color: white;
            """)
            w.textChanged.connect(self._mark_modified)
            self._bg_widgets[key] = w
            form.addRow(QLabel(label + ":"), w)

        # 装备
        equip_group = QGroupBox("装备与武器 (JSON格式)")
        equip_layout = QVBoxLayout(equip_group)
        self._equip_edit = QTextEdit()
        self._equip_edit.setStyleSheet("""
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 8px;
            color: white;
            font-family: 'Consolas', monospace;
        """)
        equip_layout.addWidget(self._equip_edit)
        form.addRow(equip_group)

        scroll.setWidget(container)
        return scroll

    def _load_data(self):
        """加载角色数据到界面"""
        c = self.character

        # 基本信息
        for key, w in self._basic_widgets.items():
            val = getattr(c, key, "")
            if key == "age":
                w.setText(str(val))
            elif key == "level":
                w.setText(str(val))
            else:
                w.setText(str(val) if val else "")

        # 属性
        if hasattr(self, '_stat_widgets'):
            for key, w in self._stat_widgets.items():
                val = getattr(c, key, 0)
                w.setValue(val)

        # COC 衍生属性
        if hasattr(self, '_derived_labels'):
            for key, lbl in self._derived_labels.items():
                val = getattr(c, key, 0)
                lbl.setText(f"{key.upper()}: {val}")

        # 技能
        if hasattr(self, '_skill_widgets'):
            for skill_name, w in self._skill_widgets.items():
                val = c.skills.get(skill_name, 0) if hasattr(c, 'skills') else 0
                w.setValue(val)

        # DND 战斗数据
        if hasattr(self, '_combat_widgets'):
            for key, w in self._combat_widgets.items():
                val = getattr(c, key, 0)
                if isinstance(w, QSpinBox):
                    w.setValue(val)
                else:
                    w.setText(str(val))

        # 法术
        if hasattr(self, '_spells_edit'):
            spells = getattr(c, 'spells', '[]')
            if isinstance(spells, str):
                self._spells_edit.setPlainText(spells)
            else:
                self._spells_edit.setPlainText(json.dumps(spells, ensure_ascii=False, indent=2))

        # 背景
        if hasattr(self, '_bg_widgets'):
            for key, w in self._bg_widgets.items():
                val = getattr(c, key, "")
                w.setPlainText(str(val))

        # 装备
        if hasattr(self, '_equip_edit'):
            equip = getattr(c, 'equipment', '[]')
            weapons = getattr(c, 'weapons', '[]')
            text = f"武器:\n{weapons}\n\n装备:\n{equip}"
            self._equip_edit.setPlainText(text)

    def _save_character(self):
        """保存角色修改"""
        c = self.character

        # 保存基本信息
        for key, w in self._basic_widgets.items():
            if key in ("age", "level"):
                try:
                    setattr(c, key, int(w.text()) if w.text() else 0)
                except ValueError:
                    pass
            else:
                setattr(c, key, w.text())

        # 保存属性
        if hasattr(self, '_stat_widgets'):
            for key, w in self._stat_widgets.items():
                setattr(c, key, w.value())

        # 保存技能
        if hasattr(self, '_skill_widgets'):
            if not hasattr(c, 'skills') or c.skills is None:
                c.skills = {}
            for skill_name, w in self._skill_widgets.items():
                c.skills[skill_name] = w.value()

        # DND 战斗数据
        if hasattr(self, '_combat_widgets'):
            for key, w in self._combat_widgets.items():
                if isinstance(w, QSpinBox):
                    setattr(c, key, w.value())
                elif isinstance(w, QLineEdit):
                    setattr(c, key, w.text())

        # 法术
        if hasattr(self, '_spells_edit'):
            c.spells = self._spells_edit.toPlainText()

        # 背景
        if hasattr(self, '_bg_widgets'):
            for key, w in self._bg_widgets.items():
                setattr(c, key, w.toPlainText())

        # 重新计算衍生值
        if self.mode == "coc":
            c._calc_derived()
            c.skills["闪避"] = c.dexterity // 2
            c.skills["母语"] = c.education

        # 保存到数据库
        from datetime import datetime
        c.updated_at = datetime.now()
        self.repo.update(self.mode, c)

        self.character_saved.emit(c)
        self._modified = False
        QMessageBox.information(self, "保存成功", f"角色「{c.name}」已保存！")
        self.accept()

    def _delete_character(self):
        """删除角色"""
        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除角色「{self.character.name}」吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.repo.delete(self.mode, self.character.id)
            self.character_deleted.emit(self.character)
            self.accept()

    def _mark_modified(self):
        """标记已修改"""
        self._modified = True
