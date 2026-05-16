"""
主窗口 — 应用的核心界面
整合导航栏、搜索栏、卡片网格、详情页、导入对话框
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QMessageBox,
)
from PySide6.QtCore import Qt

from .navigation import NavigationPanel
from .search_bar import SearchBar
from .card_grid import CardGrid
from .detail_view import DetailDialog
from .import_dialog import ImportDialog
from .export_dialog import ExportDialog
from .settings_dialog import SettingsDialog
from .theme_manager import apply_theme, load_settings
from ..database.repository import CharacterRepository
from ..plugin.plugin_manager import PluginManager

import ctypes
from ctypes import wintypes


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.current_mode = "coc"

        # 数据层
        self.repository = CharacterRepository()

        # 插件管理器
        self.plugin_manager = PluginManager(app)

        self.setWindowTitle("🎲 COC & DND 角色卡管理器")
        self.setMinimumSize(960, 640)
        self.resize(1200, 750)

        # 加载用户主题设置
        self._load_saved_theme()

        self._setup_ui()
        self._setup_connections()

        # 加载插件
        self.plugin_manager.load_all_plugins()

        # 加载角色数据
        self._refresh_characters()

        # 通知插件 UI 就绪
        self.plugin_manager.notify_ui_ready(self)

    def _setup_ui(self):
        """搭建界面"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== 左侧导航栏 =====
        self.nav_panel = NavigationPanel()
        main_layout.addWidget(self.nav_panel)

        # ===== 右侧内容区 =====
        content_area = QWidget()
        content_area.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # -- 顶部工具栏 --
        top_bar = QWidget()
        top_bar.setStyleSheet("background: transparent;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # 模式标题
        self._mode_title = QLabel("🎭 COC 角色管理")
        self._mode_title.setObjectName("titleLabel")
        self._mode_title.setStyleSheet("font-size: 20px; padding: 16px 20px 4px 20px;")
        top_layout.addWidget(self._mode_title)

        top_layout.addStretch()

        # 导入按钮
        self._import_btn = QPushButton("📥 导入")
        self._import_btn.setObjectName("actionButton")
        self._import_btn.clicked.connect(self._open_import_dialog)
        top_layout.addWidget(self._import_btn)

        # 新建按钮
        self._new_btn = QPushButton("➕ 新建")
        self._new_btn.setObjectName("actionButton")
        self._new_btn.clicked.connect(self._open_new_character_dialog)
        top_layout.addWidget(self._new_btn)

        # 导出按钮
        self._export_btn = QPushButton("📤 导出")
        self._export_btn.setObjectName("actionButton")
        self._export_btn.clicked.connect(self._open_export_dialog)
        top_layout.addWidget(self._export_btn)

        content_layout.addWidget(top_bar)

        # -- 标签页容器（角色列表 + 插件页面）--
        from PySide6.QtWidgets import QTabWidget, QWidget as QW
        self._content_tabs = QTabWidget()
        self._content_tabs.setStyleSheet("""
            QTabWidget::pane { background: transparent; border: none; }
            QTabBar::tab {
                background: transparent; color: rgba(255,255,255,0.4);
                border: none; padding: 6px 18px; font-size: 13px;
            }
            QTabBar::tab:selected { color: white; border-bottom: 2px solid #6c63ff; }
            QTabBar::tab:hover { color: rgba(255,255,255,0.7); }
        """)
        self._content_tabs.currentChanged.connect(self._on_tab_changed)

        # 默认角色列表页
        default_tab = QW()
        default_layout = QVBoxLayout(default_tab)
        default_layout.setContentsMargins(0, 0, 0, 0)
        default_layout.setSpacing(0)

        self.search_bar = SearchBar(self.current_mode)
        default_layout.addWidget(self.search_bar)

        self.card_grid = CardGrid()
        self.card_grid.card_clicked.connect(self._open_detail_view)
        default_layout.addWidget(self.card_grid)

        self._content_tabs.addTab(default_tab, "🃏 角色列表")
        content_layout.addWidget(self._content_tabs)

        main_layout.addWidget(content_area, 1)

    def _setup_connections(self):
        """连接信号"""
        self.nav_panel.mode_changed.connect(self.switch_mode)
        self.nav_panel.settings_requested.connect(self._open_settings)
        self.search_bar.search_changed.connect(self._refresh_characters)

    def _on_tab_changed(self, index):
        """标签页切换时，如果是角色列表页则刷新"""
        if index == 0:
            self._refresh_characters()

    def switch_mode(self, mode):
        """切换 COC / DND 模式"""
        self.current_mode = mode
        self.search_bar.set_mode(mode)

        if mode == "coc":
            self._mode_title.setText("🎭 COC 角色管理")
        else:
            self._mode_title.setText("🐉 DND 角色管理")

        self._refresh_characters()

        # 通知插件
        self.plugin_manager.notify_mode_switch(mode)

    def _refresh_characters(self):
        """刷新卡片网格（根据当前搜索条件加载角色）"""
        params = self.search_bar.get_search_params()
        filters = params["filters"]

        # 使用仓库搜索
        characters = self.repository.search(
            mode=self.current_mode,
            keyword=params["keyword"],
            filters=filters,
            sort_by=params["sort_by"],
            sort_order=params["sort_order"],
        )

        # 通知插件（允许插件修改搜索结果）
        characters = self.plugin_manager.notify_search(
            params["keyword"], filters, characters
        )

        self.card_grid.display_characters(characters)

    def _open_detail_view(self, character):
        """打开角色详情"""
        dialog = DetailDialog(character, self.current_mode, self.repository, self)
        dialog.character_saved.connect(self._on_character_saved)
        dialog.character_deleted.connect(self._on_character_deleted)
        dialog.exec()

    def _on_character_saved(self, character):
        """角色保存后的处理"""
        self.plugin_manager.notify_character_updated(character)
        self._refresh_characters()

    def _on_character_deleted(self, character):
        """角色删除后的处理"""
        self.plugin_manager.notify_character_deleted(character)
        self._refresh_characters()

    def _set_dark_title_bar(self):
        """调用 Windows API 将标题栏设为深色"""
        try:
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            hwnd = int(self.winId())
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                wintypes.HWND(hwnd),
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
        except Exception:
            pass

    def showEvent(self, event):
        """窗口显示后设置深色标题栏"""
        super().showEvent(event)
        self._set_dark_title_bar()

    def _load_saved_theme(self):
        """加载保存的主题设置"""
        settings = load_settings()
        theme = settings.get("theme", "深空暗黑")
        apply_theme(self, theme)

    def _open_export_dialog(self):
        """打开导出对话框"""
        dialog = ExportDialog(self.current_mode, self.repository, self)
        dialog.exec()

    def _open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self, self)
        dialog.exec()

    def _open_import_dialog(self):
        """打开导入对话框"""
        dialog = ImportDialog(self.current_mode, self.repository, self)
        # 如果导入时切换了模式，同步
        dialog.mode = self.current_mode
        if dialog.exec():
            # 导入成功后刷新
            self._refresh_characters()

    def _open_new_character_dialog(self):
        """打开新建角色对话框"""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(
            self, "新建角色", "请输入角色名称:",
        )
        if not ok or not name.strip():
            return

        # 创建角色对象
        if self.current_mode == "coc":
            from ..models.coc_character import COCCharacter
            char = COCCharacter()
        else:
            from ..models.dnd_character import DNDCharacter
            char = DNDCharacter()

        char.name = name.strip()

        # 保存到数据库
        char_id = self.repository.add(self.current_mode, char)
        if char_id:
            char.id = char_id
            self.plugin_manager.notify_character_created(char)
            QMessageBox.information(self, "创建成功", f"角色「{name}」已创建！")
            # 打开详情页让用户完善信息
            self._open_detail_view(char)
            self._refresh_characters()

    # ======== 插件注入接口 ========

    def add_plugin_menu_item(self, menu_name, item_text, callback):
        """
        添加插件菜单项（供插件调用）
        """
        # 暂时将所有插件菜单放在顶部工具栏右侧
        # 后续可以改为真正的菜单栏
        btn = QPushButton(item_text)
        btn.setObjectName("sortButton")
        btn.clicked.connect(callback)
        # 查找顶部工具栏并添加
        # 简单实现：把按钮追加到 import/new 按钮后面
        parent = self._import_btn.parent()
        if parent:
            layout = parent.layout()
            if layout:
                layout.addWidget(btn)

    def add_plugin_toolbar_button(self, text, icon_path=None, callback=None):
        """
        添加插件工具栏按钮（供插件调用）
        """
        btn = QPushButton(text)
        btn.setObjectName("sortButton")
        if callback:
            btn.clicked.connect(callback)
        parent = self._import_btn.parent()
        if parent:
            layout = parent.layout()
            if layout:
                layout.addWidget(btn)

    def add_plugin_tab(self, tab_id, title, widget):
        """添加插件标签页（供插件调用）"""
        if hasattr(self, '_content_tabs'):
            self._content_tabs.addTab(widget, title)

    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        self.repository.close()
        super().closeEvent(event)
