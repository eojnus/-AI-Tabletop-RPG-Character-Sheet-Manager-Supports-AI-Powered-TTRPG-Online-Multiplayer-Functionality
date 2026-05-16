"""
角色创建向导 — 将6个步骤串联成完整的创建流程
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QLineEdit, QMessageBox,
)
from PySide6.QtCore import Qt

from .step_widgets import (
    StepGameMode, StepChooseClass, StepAttributes,
    StepSkills, StepEquipment, StepConfirm,
)
from character_manager.models.coc_character import COCCharacter
from character_manager.models.dnd_character import DNDCharacter


class CharacterCreatorWizard(QWidget):
    """角色创建向导主控件（可嵌入标签页）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.character_created = False

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # === 步骤指示器 ===
        self._step_indicator = QLabel()
        self._step_indicator.setStyleSheet("""
            font-size: 12px;
            color: rgba(255,255,255,0.4);
            padding: 4px 0;
        """)
        layout.addWidget(self._step_indicator)

        # === 角色名称输入 ===
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("角色名称:"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("输入角色名称…")
        self._name_input.setMaxLength(30)
        name_row.addWidget(self._name_input, stretch=1)
        layout.addLayout(name_row)

        # === 步骤内容 ===
        self._stack = QStackedWidget()
        self._step_widgets = []

        step1 = StepGameMode()
        step1.mode_selected.connect(self._on_mode_selected)
        step2 = StepChooseClass()
        step3 = StepAttributes()
        step4 = StepSkills()
        step5 = StepEquipment()
        step6 = StepConfirm()

        self._steps = [step1, step2, step3, step4, step5, step6]
        for w in self._steps:
            self._stack.addWidget(w)
            self._step_widgets.append(w)

        layout.addWidget(self._stack, stretch=1)

        # === 导航按钮 ===
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(12)

        self._back_btn = QPushButton("← 上一步")
        self._back_btn.setObjectName("sortButton")
        self._back_btn.clicked.connect(self._go_back)
        nav_layout.addWidget(self._back_btn)

        nav_layout.addStretch()

        self._step_label = QLabel("")
        self._step_label.setStyleSheet("color: rgba(255,255,255,0.5);")
        nav_layout.addWidget(self._step_label)

        self._next_btn = QPushButton("下一步 →")
        self._next_btn.setObjectName("actionButton")
        self._next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self._next_btn)

        layout.addLayout(nav_layout)

        # 初始化为第一步
        self._current_step = 0
        self._update_ui()

    def _update_ui(self):
        """更新界面状态"""
        total = len(self._steps)
        current = self._current_step + 1
        self._step_indicator.setText(
            f"{'─' * 20}  第 {current}/{total} 步  {'─' * 20}"
        )
        self._step_label.setText(f"({current}/{total})")

        self._back_btn.setEnabled(self._current_step > 0)
        self._stack.setCurrentIndex(self._current_step)

        # 最后一步按钮文字变化
        if self._current_step == len(self._steps) - 1:
            self._next_btn.setText("✅ 创建角色")
        else:
            self._next_btn.setText("下一步 →")

        # 第一步没有上一步
        self._back_btn.setVisible(self._current_step > 0)

        # 切换模式时更新后续步骤
        self._sync_steps()

    def _sync_steps(self):
        """同步游戏模式到各步骤"""
        mode = self._get_mode()
        if mode:
            for step in self._steps[2:]:
                if hasattr(step, 'set_mode'):
                    step.set_mode(mode)
            self._step_widgets[1].set_mode(mode)

    def _get_mode(self):
        """获取当前选择的游戏模式"""
        step1 = self._steps[0]
        if hasattr(step1, 'get_mode'):
            return step1.get_mode()
        return None

    def _on_mode_selected(self, mode):
        """选择模式后自动进入下一步"""
        self._current_step = 1
        self._sync_steps()
        self._update_ui()

    def _go_back(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._update_ui()

    def _go_next(self):
        step = self._steps[self._current_step]

        # 验证当前步骤
        if self._current_step == 0:
            mode = step.get_mode()
            if not mode:
                QMessageBox.warning(self, "提示", "请选择游戏模式（COC 或 DND）！")
                return
            if not self._name_input.text().strip():
                QMessageBox.warning(self, "提示", "请输入角色名称！")
                return

        elif self._current_step == 1:
            if not step.validate():
                QMessageBox.warning(self, "提示", "请先选择职业/种族！")
                return
            # 传递选择给后续步骤
            selection = step.get_selection()
            attrs = self._steps[2].attribute_values or {}
            self._steps[3].set_data(self._get_mode(), selection, attrs)
            self._steps[4].set_data(self._get_mode(), selection)

        elif self._current_step == 2:
            if not step.validate():
                QMessageBox.warning(self, "提示", "请先生成属性！")
                return

        elif self._current_step == 3:
            if hasattr(step, 'validate') and not step.validate():
                QMessageBox.warning(self, "提示", "技能点数超支了！请调整后再继续。")
                return

        elif self._current_step == 5:
            # 最后一步：创建角色
            self._create_character()
            return

        # 如果是技能步骤的最后阶段（个人兴趣已分配完），直接跳确认
        if self._current_step == 3 and hasattr(step, '_phase'):
            pass  # 不做特殊处理，等用户提交

        # 传递数据到确认页
        if self._current_step == 4:
            confirm = self._steps[5]
            mode = self._get_mode()
            name = self._name_input.text().strip()
            selection = self._steps[1].get_selection()
            attrs = self._steps[2].get_attributes()
            skills = self._steps[3].get_skills()
            equipment = self._steps[4].get_equipment()
            confirm.set_summary(mode, name, selection, attrs, skills, equipment)

        if self._current_step < len(self._steps) - 1:
            self._current_step += 1
            self._update_ui()

    def _reset_wizard(self):
        """重置向导到初始状态"""
        self._name_input.clear()
        self._current_step = 0
        for i in range(len(self._steps)):
            old = self._steps[i]
            self._stack.removeWidget(old)
            old.deleteLater()
        from .step_widgets import (
            StepGameMode, StepChooseClass, StepAttributes,
            StepSkills, StepEquipment, StepConfirm,
        )
        new_steps = [
            StepGameMode(), StepChooseClass(), StepAttributes(),
            StepSkills(), StepEquipment(), StepConfirm(),
        ]
        new_steps[0].mode_selected.connect(self._on_mode_selected)
        for w in new_steps:
            self._stack.addWidget(w)
        self._steps = new_steps
        self._step_widgets = new_steps
        self._update_ui()

    def _create_character(self):
        """创建角色并保存到数据库"""
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入角色名称！")
            return

        mode = self._get_mode()
        selection = self._steps[1].get_selection()
        attrs = self._steps[2].get_attributes()
        skills = self._steps[3].get_skills()
        equipment = self._steps[4].get_equipment()

        try:
            if mode == "coc":
                char = COCCharacter()
                # 基础信息
                char.name = name
                char.occupation = selection.get("occupation", "")
                # 属性
                attr_map = {
                    "力量": "strength", "体质": "constitution", "意志": "power",
                    "敏捷": "dexterity", "外貌": "appearance", "体型": "size",
                    "智力": "intelligence", "教育": "education",
                }
                for cn, en in attr_map.items():
                    if cn in attrs:
                        setattr(char, en, attrs[cn])

                # 技能
                if skills:
                    for skill_name, val in skills.items():
                        char.skills[skill_name] = val

                # 装备
                char.equipment = equipment
                char._calc_derived()

            else:
                char = DNDCharacter()
                char.name = name
                char.race = selection.get("race", "人类")
                char.class_name = selection.get("class", "战士")
                char.level = selection.get("level", 1)
                char.background = selection.get("background", "")
                char.alignment = selection.get("alignment", "绝对中立")

                attr_map = {
                    "力量": "strength", "敏捷": "dexterity", "体质": "constitution",
                    "智力": "intelligence", "感知": "wisdom", "魅力": "charisma",
                }
                for cn, en in attr_map.items():
                    if cn in attrs:
                        setattr(char, en, attrs[cn])

                # 技能
                if skills:
                    char.skills = skills

                char.equipment = equipment

            # 保存到数据库
            if self.main_window and hasattr(self.main_window, 'repository'):
                repo = self.main_window.repository
                char_id = repo.add(mode, char)
                if char_id:
                    char.id = char_id
                    self.character_created = True
                    QMessageBox.information(
                        self, "🎉 创建成功",
                        f"角色「{name}」已成功创建并保存！"
                    )
                    # 刷新主窗口卡片显示
                    if hasattr(self.main_window, '_refresh_characters'):
                        self.main_window._refresh_characters()
                    # 创建成功后重置向导
                    self._reset_wizard()
                    return

            QMessageBox.warning(self, "错误", "保存角色失败！")

        except Exception as e:
            QMessageBox.critical(self, "创建失败", f"创建角色时出错:\n{str(e)}")
