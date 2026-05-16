"""
设置对话框 — 主题/字体/字号配置
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QWidget, QGroupBox, QSlider,
    QLineEdit, QTabWidget, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .theme_manager import (
    THEMES, load_settings, save_settings, DEFAULT_THEME,
    DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, apply_theme,
)


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowTitle("⚙️ 设置")
        self.setMinimumSize(560, 480)
        self.setModal(True)
        self.setObjectName("detailWindow")

        # 当前设置
        self.settings = load_settings()
        self.current_theme = self.settings.get("theme", DEFAULT_THEME)
        self.current_font = self.settings.get("font_family", DEFAULT_FONT_FAMILY)
        self.current_size = self.settings.get("font_size", DEFAULT_FONT_SIZE)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 16)
        layout.setSpacing(10)

        # 标题
        title = QLabel("⚙️ 设置")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # 标签页
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { background: transparent; border: none; padding: 8px; }
            QTabBar::tab {
                background: transparent; color: rgba(255,255,255,0.4);
                border: none; padding: 8px 18px; font-size: 13px;
            }
            QTabBar::tab:selected { color: white; border-bottom: 2px solid #6c63ff; }
            QTabBar::tab:hover { color: rgba(255,255,255,0.7); }
        """)

        # ---------- 外观标签页 ----------
        appearance_tab = QWidget()
        app_layout = QVBoxLayout(appearance_tab)
        app_layout.setSpacing(12)

        theme_group = QGroupBox("🎨 界面主题")
        theme_layout = QVBoxLayout(theme_group)
        theme_desc = QLabel("选择你喜欢的配色方案：")
        theme_desc.setObjectName("statLabel")
        theme_layout.addWidget(theme_desc)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(list(THEMES.keys()))
        self._theme_combo.setCurrentText(self.current_theme)
        self._theme_combo.currentTextChanged.connect(self._preview_theme)
        theme_layout.addWidget(self._theme_combo)

        self._preview_widget = QWidget()
        self._preview_widget.setFixedHeight(40)
        self._preview_widget.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {THEMES[self.current_theme]['colors']['bg_start']},"
            f"stop:1 {THEMES[self.current_theme]['colors']['bg_end']});"
            f"border-radius:10px; border:1px solid {THEMES[self.current_theme]['colors']['border']};"
        )
        theme_layout.addWidget(self._preview_widget)
        app_layout.addWidget(theme_group)

        font_group = QGroupBox("🔤 字体设置")
        font_layout = QVBoxLayout(font_group)
        fr1 = QHBoxLayout()
        fr1.addWidget(QLabel("字体:"))
        self._font_combo = QComboBox()
        self._font_combo.setEditable(True)
        self._font_combo.addItems([
            "Microsoft YaHei", "Microsoft JhengHei", "PingFang SC",
            "Noto Sans SC", "SimSun", "SimHei", "DengXian",
            "Segoe UI", "Arial", "Consolas",
        ])
        self._font_combo.setCurrentText(self.current_font)
        fr1.addWidget(self._font_combo, stretch=1)
        font_layout.addLayout(fr1)

        fr2 = QHBoxLayout()
        fr2.addWidget(QLabel("字号:"))
        self._size_spin = QSpinBox()
        self._size_spin.setRange(10, 24)
        self._size_spin.setValue(self.current_size)
        self._size_spin.setSuffix(" px")
        fr2.addWidget(self._size_spin)
        self._size_slider = QSlider(Qt.Horizontal)
        self._size_slider.setRange(10, 24)
        self._size_slider.setValue(self.current_size)
        self._size_slider.valueChanged.connect(self._size_spin.setValue)
        self._size_spin.valueChanged.connect(self._size_slider.setValue)
        fr2.addWidget(self._size_slider, stretch=1)
        font_layout.addLayout(fr2)

        self._font_preview = QLabel("中文字体预览 Aa 123 — The quick brown fox")
        self._font_preview.setAlignment(Qt.AlignCenter)
        self._font_preview.setStyleSheet(
            f"background: rgba(255,255,255,0.05); border-radius:8px;"
            f"padding:12px; font-family:'{self.current_font}'; font-size:{self.current_size}px;"
        )
        font_layout.addWidget(self._font_preview)
        self._font_combo.currentTextChanged.connect(self._update_font_preview)
        self._size_spin.valueChanged.connect(self._update_font_preview)
        app_layout.addWidget(font_group)
        app_layout.addStretch()
        tabs.addTab(appearance_tab, "🎨 外观")

        # ---------- 插件设置标签页 ----------
        plugin_tab = QWidget()
        plug_layout = QVBoxLayout(plugin_tab)
        plug_layout.setSpacing(12)

        plug_title = QLabel("可在此处设置已安装插件的参数：")
        plug_title.setStyleSheet("font-size:13px; color: rgba(255,255,255,0.6);")

        # 遍历已加载的插件，显示它们的设置
        if hasattr(self.main_window, 'plugin_manager'):
            pm = self.main_window.plugin_manager
            loaded = pm.get_all_plugins()
            has_plugin_settings = False

            for pinfo in loaded:
                plug = pinfo["instance"]
                # 检查插件是否有 settings_widget 方法
                if hasattr(plug, 'get_settings_widget'):
                    widget = plug.get_settings_widget()
                    if widget:
                        has_plugin_settings = True
                        gb = QGroupBox(f"🔌 {plug.PLUGIN_NAME} v{plug.PLUGIN_VERSION}")
                        gb.setLayout(QVBoxLayout())
                        gb.layout().addWidget(widget)
                        plug_layout.addWidget(gb)
                # AI 跑团插件的内置设置（即使没有 settings_widget 方法）
                if pinfo["name"] == "trpg_ai_keeper":
                    has_plugin_settings = True
                    gb = QGroupBox(f"🔌 {plug.PLUGIN_NAME} v{plug.PLUGIN_VERSION}")
                    plug_layout.addWidget(gb)
                    plug_layout.addWidget(QLabel("DeepSeek API 设置："))
                    self._plugin_api_key = QLineEdit()
                    self._plugin_api_key.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                    self._plugin_api_key.setText(self.settings.get("ai_keeper_api_key", ""))
                    plug_layout.addWidget(QLabel("API Key:"))
                    plug_layout.addWidget(self._plugin_api_key)

                    self._plugin_model = QComboBox()
                    self._plugin_model.addItems(["deepseek-v4-flash (快速便宜)", "deepseek-v4-pro (更强)"])
                    current_model = self.settings.get("ai_keeper_model", "deepseek-v4-flash")
                    self._plugin_model.setCurrentIndex(0 if "flash" in current_model else 1)
                    plug_layout.addWidget(QLabel("模型:"))
                    plug_layout.addWidget(self._plugin_model)

            if not has_plugin_settings:
                plug_layout.addWidget(QLabel("📭 当前没有需要额外设置的插件。"))
                plug_layout.addWidget(QLabel("安装插件后，其配置选项会自动出现在这里。"))
        else:
            plug_layout.addWidget(QLabel("📭 无法访问插件管理器。"))

        plug_layout.addStretch()
        tabs.addTab(plugin_tab, "🔌 插件")

        layout.addWidget(tabs, stretch=1)

        # ===== 底部按钮 =====
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("↺ 恢复默认")
        reset_btn.setObjectName("sortButton")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("sortButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        apply_btn = QPushButton("✅ 应用")
        apply_btn.setObjectName("actionButton")
        apply_btn.clicked.connect(self._apply_settings)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def _preview_theme(self, theme_name):
        """预览主题颜色"""
        colors = THEMES[theme_name]["colors"]
        self._preview_widget.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {colors['bg_start']}, stop:1 {colors['bg_end']}); "
            f"border-radius: 10px; "
            f"border: 1px solid {colors['border']};"
        )

    def _update_font_preview(self):
        """更新字体预览"""
        font = self._font_combo.currentText()
        size = self._size_spin.value()
        self._font_preview.setStyleSheet(
            f"background: rgba(255,255,255,0.05); border-radius: 8px; "
            f"padding: 12px; font-family: '{font}'; "
            f"font-size: {size}px; color: rgba(255,255,255,0.6);"
        )

    def _reset_defaults(self):
        """恢复默认设置"""
        self._theme_combo.setCurrentText(DEFAULT_THEME)
        self._font_combo.setCurrentText(DEFAULT_FONT_FAMILY)
        self._size_spin.setValue(DEFAULT_FONT_SIZE)

    def _apply_settings(self):
        """应用设置"""
        theme = self._theme_combo.currentText()
        font = self._font_combo.currentText()
        size = self._size_spin.value()

        # 保存外观设置
        self.settings["theme"] = theme
        self.settings["font_family"] = font
        self.settings["font_size"] = size

        # 保存插件设置（AI 跑团助手）
        if hasattr(self, '_plugin_api_key'):
            self.settings["ai_keeper_api_key"] = self._plugin_api_key.text().strip()
        if hasattr(self, '_plugin_model'):
            model_text = self._plugin_model.currentText()
            self.settings["ai_keeper_model"] = "deepseek-v4-flash" if "flash" in model_text else "deepseek-v4-pro"

        save_settings(self.settings)

        # 应用主题到主窗口
        apply_theme(self.main_window, theme)

        QMessageBox.information(self, "设置已保存", "所有设置已保存！\nAI 跑团插件的 API Key 和模型选择已更新。")
        self.accept()
