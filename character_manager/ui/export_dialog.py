"""
导出对话框 — 选择角色并导出为格式化文本
"""
import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QTextEdit, QWidget,
    QMessageBox, QFileDialog, QSplitter, QAbstractItemView,
)
from PySide6.QtCore import Qt

from ..database.repository import CharacterRepository
from ..models.coc_character import COCCharacter
from ..models.dnd_character import DNDCharacter


class ExportDialog(QDialog):
    """角色导出对话框"""

    def __init__(self, mode, repository, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.repo = repository
        self.setWindowTitle("📤 导出角色卡")
        self.setMinimumSize(720, 520)
        self.setModal(True)
        self.setObjectName("detailWindow")

        self._all_characters = []
        self._setup_ui()
        self._load_characters()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # 标题
        title = QLabel("📤 导出角色卡")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        hint = QLabel("选择要导出的角色，导出为可重新导入的格式化文本。")
        hint.setObjectName("subtitleLabel")
        layout.addWidget(hint)

        # 分割面板：左侧角色列表，右侧预览
        splitter = QSplitter(Qt.Horizontal)

        # ===== 左侧：角色列表 =====
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)

        # 搜索框
        self._search_input = QLineEdit()
        self._search_input.setObjectName("searchBar")
        self._search_input.setPlaceholderText("🔍 搜索角色…")
        self._search_input.textChanged.connect(self._filter_characters)
        left_layout.addWidget(self._search_input)

        # 角色列表（可多选）
        self._char_list = QListWidget()
        self._char_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self._char_list.itemSelectionChanged.connect(self._update_preview)
        left_layout.addWidget(self._char_list)

        # 选择计数
        self._count_label = QLabel("已选: 0 个角色")
        self._count_label.setObjectName("statLabel")
        left_layout.addWidget(self._count_label)

        splitter.addWidget(left_panel)

        # ===== 右侧：预览区 =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        preview_label = QLabel("📄 导出预览：")
        preview_label.setStyleSheet("font-weight: 500;")
        right_layout.addWidget(preview_label)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setPlaceholderText("选择左侧角色后，此处显示导出预览…")
        right_layout.addWidget(self._preview)

        splitter.addWidget(right_panel)
        splitter.setSizes([280, 440])
        layout.addWidget(splitter, stretch=1)

        # ===== 底部按钮 =====
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QLabel("💡 按住 Ctrl 可多选"))

        self._select_all_btn = QPushButton("全选")
        self._select_all_btn.setObjectName("sortButton")
        self._select_all_btn.clicked.connect(self._select_all)
        btn_layout.addWidget(self._select_all_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("sortButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        export_btn = QPushButton("💾 导出为文件")
        export_btn.setObjectName("actionButton")
        export_btn.clicked.connect(self._export_to_file)
        btn_layout.addWidget(export_btn)

        copy_btn = QPushButton("📋 复制到剪贴板")
        copy_btn.setObjectName("actionButton")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_layout.addWidget(copy_btn)

        layout.addLayout(btn_layout)

    def _load_characters(self):
        """加载角色列表"""
        self._all_characters = self.repo.get_all(self.mode)
        self._filter_characters()

    def _filter_characters(self):
        """根据搜索词过滤角色列表"""
        keyword = self._search_input.text().strip().lower()
        self._char_list.clear()
        self._item_to_char = {}

        for char in self._all_characters:
            if keyword and keyword not in char.name.lower():
                continue
            summary = char.get_card_summary()
            label = f"{summary['name']}  |  {summary['subtitle']}"
            item = self._char_list.addItem(label)
            self._item_to_char[label] = char

        self._update_count()

    def _update_count(self):
        """更新选中计数"""
        count = len(self._char_list.selectedItems())
        self._count_label.setText(f"已选: {count} 个角色")

    def _get_selected_characters(self):
        """获取选中的角色列表"""
        return [
            self._item_to_char[item.text()]
            for item in self._char_list.selectedItems()
            if item.text() in self._item_to_char
        ]

    def _update_preview(self):
        """更新选中角色的预览文本"""
        self._update_count()
        chars = self._get_selected_characters()
        if not chars:
            self._preview.setPlainText("（请选择要导出的角色）")
            return

        lines = []
        for i, char in enumerate(chars):
            if i > 0:
                lines.append("")
                lines.append("=" * 50)
                lines.append("")
            lines.append(self._character_to_text(char))

        self._preview.setPlainText("\n".join(lines))

    def _character_to_text(self, character):
        """将单个角色转换为格式化文本"""
        lines = []
        lines.append(f"姓名: {character.name}")

        if isinstance(character, COCCharacter):
            lines.append(f"职业: {character.occupation}")
            lines.append(f"年龄: {character.age}  性别: {character.gender}")
            lines.append(f"玩家: {character.player_name}")
            lines.append("")
            lines.append(f"力量: {character.strength}  体质: {character.constitution}  意志: {character.power}")
            lines.append(f"敏捷: {character.dexterity}  外貌: {character.appearance}  体型: {character.size}")
            lines.append(f"智力: {character.intelligence}  教育: {character.education}")
            lines.append(f"HP: {character.hp}  SAN: {character.san}  MP: {character.mp}  幸运: {character.luck}")
            lines.append("")
            # 技能
            skill_strs = []
            for name, val in sorted(character.skills.items()):
                if val > 0:
                    skill_strs.append(f"{name} {val}")
            if skill_strs:
                lines.append("技能: " + ", ".join(skill_strs))

        else:  # DND
            lines.append(f"种族: {character.race}  职业: {character.class_name}  Lv.{character.level}")
            lines.append(f"阵营: {character.alignment}  背景: {character.background}")
            lines.append(f"年龄: {character.age}  性别: {character.gender}")
            lines.append("")
            lines.append(f"力量: {character.strength}  敏捷: {character.dexterity}  体质: {character.constitution}")
            lines.append(f"智力: {character.intelligence}  感知: {character.wisdom}  魅力: {character.charisma}")
            lines.append(f"HP: {character.hp_current}/{character.hp_max}  AC: {character.armor_class}  速度: {character.speed}ft")

        return "\n".join(lines)

    def _select_all(self):
        """全选/取消全选"""
        if self._char_list.count() == len(self._char_list.selectedItems()):
            self._char_list.clearSelection()
        else:
            self._char_list.selectAll()

    def _export_to_file(self):
        """导出为文件"""
        chars = self._get_selected_characters()
        if not chars:
            QMessageBox.warning(self, "提示", "请先在左侧选择要导出的角色！")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "保存导出文件", "characters.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        if not path:
            return

        text = self._preview.toPlainText()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        QMessageBox.information(self, "导出成功",
            f"已导出 {len(chars)} 个角色到:\n{path}")
        self.accept()

    def _copy_to_clipboard(self):
        """复制到剪贴板"""
        chars = self._get_selected_characters()
        if not chars:
            QMessageBox.warning(self, "提示", "请先在左侧选择要导出的角色！")
            return

        from PySide6.QtGui import QClipboard
        QApplication = self.window().app if hasattr(self.window(), 'app') else None
        clipboard = self.window().app.clipboard() if QApplication else None
        
        # 直接使用 QApplication 获取剪贴板
        from PySide6.QtWidgets import QApplication as QA
        QA.clipboard().setText(self._preview.toPlainText())

        QMessageBox.information(self, "已复制",
            f"已复制 {len(chars)} 个角色的文本到剪贴板！")
