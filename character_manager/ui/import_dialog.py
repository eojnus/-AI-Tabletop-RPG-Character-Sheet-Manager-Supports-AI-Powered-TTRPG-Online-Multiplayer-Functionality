"""
导入对话框 — 粘贴文本 → 自动解析 → 预览 → 保存
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QWidget, QGroupBox, QFormLayout, QMessageBox,
    QFrame,
)
from PySide6.QtCore import Qt

from ..parser.text_parser import TextParser
from ..models.coc_character import COCCharacter
from ..models.dnd_character import DNDCharacter


class ImportDialog(QDialog):
    """文本导入对话框"""

    def __init__(self, mode, repository, parent=None):
        super().__init__(parent)
        self.setObjectName("detailWindow")
        self.mode = mode
        self.repo = repository
        self.parsed_character = None
        self.parser = TextParser()

        self.setWindowTitle("📥 导入角色卡 — 粘贴文字自动识别")
        self.setMinimumSize(640, 520)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # 标题与说明
        title = QLabel("📥 导入角色卡")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        hint = QLabel(
            "将角色卡文字粘贴到下方输入框，系统会自动识别并填充角色数据。\n"
            "支持格式: 姓名: xxx  职业: xxx  力量: 60 …… 等条目格式\n"
            "未填写的字段将自动使用默认值。"
        )
        hint.setObjectName("subtitleLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # 文本输入区
        input_label = QLabel("📋 粘贴角色卡文字：")
        input_label.setStyleSheet("font-weight: 500; color: rgba(255,255,255,0.7);")
        layout.addWidget(input_label)

        self._text_input = QTextEdit()
        self._text_input.setPlaceholderText(
            "示例：\n"
            "姓名: 张灵均\n"
            "职业: 私家侦探\n"
            "年龄: 28\n"
            "力量: 60  敏捷: 70  意志: 65\n"
            "体质: 50  体型: 55  外貌: 40\n"
            "智力: 75  教育: 70\n"
            "侦查: 80  图书馆使用: 70  格斗(斗殴): 60\n"
            "射击(手枪): 50  潜行: 40  聆听: 60"
        )
        layout.addWidget(self._text_input)

        # 解析按钮
        parse_btn = QPushButton("🔍 自动识别")
        parse_btn.setObjectName("actionButton")
        parse_btn.clicked.connect(self._parse_text)
        layout.addWidget(parse_btn, alignment=Qt.AlignCenter)

        # 分隔
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # 解析结果预览
        preview_label = QLabel("📄 识别结果预览：")
        preview_label.setStyleSheet("font-weight: 500; color: rgba(255,255,255,0.7);")
        layout.addWidget(preview_label)

        self._preview_area = QTextEdit()
        self._preview_area.setReadOnly(True)
        self._preview_area.setPlaceholderText("点击「自动识别」后，此处显示解析结果…")
        layout.addWidget(self._preview_area)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("sortButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self._save_btn = QPushButton("💾 确认保存")
        self._save_btn.setObjectName("actionButton")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._save_character)
        btn_layout.addWidget(self._save_btn)

        layout.addLayout(btn_layout)

    def _parse_text(self):
        """解析粘贴的文本"""
        text = self._text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请先粘贴角色卡文字！")
            return

        # 自动检测模式（如果当前模式不匹配，提示用户）
        detected_mode = TextParser.detect_mode(text)
        if detected_mode and detected_mode != self.mode:
            reply = QMessageBox.question(
                self, "模式不匹配",
                f"检测到这段文字是「{'COC' if detected_mode == 'coc' else 'DND'}」格式，"
                f"但当前处于「{'COC' if self.mode == 'coc' else 'DND'}」模式。\n"
                f"是否切换到{'COC' if detected_mode == 'coc' else 'DND'}模式重新导入？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.mode = detected_mode
                # 通知父窗口切换模式（通过信号机制，此处直接处理）
                parent = self.parent()
                if parent and hasattr(parent, 'switch_mode'):
                    parent.switch_mode(detected_mode)

        # 执行解析
        try:
            result = self.parser.parse(text, self.mode)
            self.parsed_character = result["character"]
            parsed_fields = result["parsed_fields"]
            errors = result["errors"]

            # 生成预览文本
            preview = self._generate_preview(self.parsed_character, parsed_fields, errors)
            self._preview_area.setPlainText(preview)
            self._save_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "解析失败", f"解析过程中出现错误:\n{str(e)}")
            self._save_btn.setEnabled(False)

    def _generate_preview(self, character, parsed_fields, errors):
        """生成解析结果预览文本"""
        lines = []

        if isinstance(character, COCCharacter):
            lines.append("🎭 COC 角色卡识别结果")
            lines.append("=" * 40)
            lines.append(f"✅ 已识别的字段: {', '.join(parsed_fields[:15])}")
            if len(parsed_fields) > 15:
                lines.append(f"   ... 及其他 {len(parsed_fields) - 15} 个字段")
            lines.append("")
            lines.append(f"📛 姓名: {character.name}")
            lines.append(f"💼 职业: {character.occupation}")
            lines.append(f"👤 年龄: {character.age}  性别: {character.gender}")
            lines.append("")
            lines.append("📊 属性:")
            lines.append(f"  STR{character.strength} CON{character.constitution} POW{character.power} DEX{character.dexterity}")
            lines.append(f"  APP{character.appearance} SIZ{character.size} INT{character.intelligence} EDU{character.education}")
            lines.append(f"  HP:{character.hp} MP:{character.mp} SAN:{character.san} 幸运:{character.luck}")
            lines.append("")
            lines.append("📋 已识别技能:")
            skill_count = sum(1 for s in character.skills.values() if s > 0)
            lines.append(f"  (共 {skill_count} 项技能有数值)")

        else:
            lines.append("🐉 DND 5e 角色卡识别结果")
            lines.append("=" * 40)
            lines.append(f"✅ 已识别的字段: {', '.join(parsed_fields[:15])}")
            if len(parsed_fields) > 15:
                lines.append(f"   ... 及其他 {len(parsed_fields) - 15} 个字段")
            lines.append("")
            lines.append(f"📛 姓名: {character.name}")
            lines.append(f"🔰 等级: {character.level}  {character.race}  {character.class_name}")
            lines.append(f"⚖️ 阵营: {character.alignment}")
            lines.append("")
            lines.append("📊 属性:")
            lines.append(f"  STR{character.strength} DEX{character.dexterity} CON{character.constitution}")
            lines.append(f"  INT{character.intelligence} WIS{character.wisdom} CHA{character.charisma}")
            mod_str = character.get_ability_modifier(character.strength)
            lines.append(f"  AC:{character.armor_class} HP:{character.hp_max} 先攻:{character.initiative:+d}")

        # 警告信息
        if errors:
            lines.append("")
            lines.append("⚠️ 注意事项:")
            for err in errors:
                lines.append(f"  {err}")

        lines.append("")
        lines.append("💡 提示: 导入完成后可在详情页中继续编辑完善。")
        return "\n".join(lines)

    def _save_character(self):
        """保存解析后的角色到数据库"""
        if not self.parsed_character:
            return

        char_id = self.repo.add(self.mode, self.parsed_character)
        if char_id:
            self.parsed_character.id = char_id
            QMessageBox.information(
                self, "导入成功",
                f"角色「{self.parsed_character.name}」已成功导入！"
            )
            self.accept()
        else:
            QMessageBox.critical(self, "导入失败", "保存到数据库时出现错误，请重试。")
