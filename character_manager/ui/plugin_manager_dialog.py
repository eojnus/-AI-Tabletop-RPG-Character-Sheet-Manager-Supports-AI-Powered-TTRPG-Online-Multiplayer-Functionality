"""
插件管理对话框 — 查看已加载/未加载的插件，勾选启用/禁用
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QWidget,
    QMessageBox,
)
from PySide6.QtCore import Qt

from ..paths import load_settings_json, save_settings_json


class PluginManagerDialog(QDialog):
    """插件管理对话框"""

    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.pm = plugin_manager
        self.setWindowTitle("🔌 插件管理")
        self.setMinimumSize(520, 400)
        self.setModal(True)
        self.setObjectName("detailWindow")

        # 读取已禁用的插件列表
        self.disabled_plugins = set(load_settings_json().get("disabled_plugins", []))

        self._setup_ui()
        self._load_plugins()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("🔌 插件管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("勾选 = 启用，取消勾选 = 禁用。\n部分插件可能需要重启才能完全生效。")
        desc.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._plugin_list = QListWidget()
        self._plugin_list.setStyleSheet("""
            QListWidget {
                background: rgba(0,0,0,0.15);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 6px 4px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background: rgba(255,255,255,0.05);
            }
        """)
        layout.addWidget(self._plugin_list, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("sortButton")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setObjectName("actionButton")
        refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

    def _load_plugins(self):
        """加载插件列表"""
        self._plugin_list.clear()
        self._checkboxes = {}
        self._items = {}

        # 发现所有插件
        discovered = self.pm.discover_plugins()
        loaded = self.pm.get_all_plugins()
        loaded_names = {p["name"] for p in loaded}

        for info in discovered:
            name = info["name"]
            is_loaded = name in loaded_names
            is_disabled = name in self.disabled_plugins

            # 构建显示内容
            if is_loaded:
                plugin = self.pm.get_plugin(name)
                version = plugin.PLUGIN_VERSION if plugin else "?"
                desc_text = plugin.PLUGIN_DESCRIPTION if plugin else ""
                status = f"✅ 已加载 v{version}"
            elif is_disabled:
                version = "?"
                desc_text = "已禁用，勾选复选框可重新启用。"
                status = "⏸️ 已禁用"
            else:
                version = "?"
                desc_text = f"加载失败: {self.pm.load_errors.get(name, '未知错误')}"
                status = "❌ 加载失败"

            # 创建条目
            widget = QWidget()
            row = QHBoxLayout(widget)
            row.setContentsMargins(8, 4, 8, 4)
            row.setSpacing(10)

            cb = QCheckBox()
            cb.setChecked(is_loaded and not is_disabled)
            cb.setEnabled(is_loaded or is_disabled or name in self.pm.load_errors)
            cb.stateChanged.connect(lambda state, n=name: self._toggle_plugin(n, state))
            self._checkboxes[name] = cb
            row.addWidget(cb)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            title_lbl = QLabel(f"📦 {name}  {status}")
            title_lbl.setStyleSheet("font-weight: 500; font-size: 13px;"
                                    if is_loaded else "font-size: 13px; color: rgba(255,255,255,0.5);")
            text_layout.addWidget(title_lbl)

            if desc_text:
                desc_lbl = QLabel(desc_text)
                desc_lbl.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.4);")
                desc_lbl.setWordWrap(True)
                text_layout.addWidget(desc_lbl)

            row.addLayout(text_layout, stretch=1)
            row.addStretch()

            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self._plugin_list.addItem(item)
            self._plugin_list.setItemWidget(item, widget)
            self._items[name] = item

        # 如果没有插件
        if not discovered:
            item = QListWidgetItem("📭 未发现任何插件\n将插件文件夹放入 plugins/ 目录")
            self._plugin_list.addItem(item)

    def _toggle_plugin(self, name, state):
        """启用/禁用插件"""
        enabled = bool(state)

        if enabled:
            # 启用：从禁用列表移除 + 尝试加载
            self.disabled_plugins.discard(name)
            if name not in {p["name"] for p in self.pm.get_all_plugins()}:
                success, msg = self.pm.load_plugin(name)
                if not success:
                    QMessageBox.warning(self, "加载失败", msg)
                    cb = self._checkboxes.get(name)
                    if cb:
                        cb.blockSignals(True)
                        cb.setChecked(False)
                        cb.blockSignals(False)
                    return
                # 通知 UI 就绪
                plugin = self.pm.get_plugin(name)
                parent = self.parent() or self.window()
                if plugin and hasattr(parent, '_content_tabs'):
                    plugin.main_window = parent
                    plugin.on_ui_ready(parent)
        else:
            # 禁用
            self.disabled_plugins.add(name)
            if name in {p["name"] for p in self.pm.get_all_plugins()}:
                # 卸载插件
                self.pm.disable_plugin(name)

        # 保存设置
        settings = load_settings_json()
        settings["disabled_plugins"] = list(self.disabled_plugins)
        save_settings_json(settings)

    def _refresh(self):
        """刷新列表"""
        self._load_plugins()
