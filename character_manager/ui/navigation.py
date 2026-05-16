"""
导航栏组件 — 左侧导航面板
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal


class NavigationPanel(QWidget):
    """左侧导航栏"""

    mode_changed = Signal(str)  # 发射 "coc" 或 "dnd"
    settings_requested = Signal()  # 打开设置

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navPanel")
        self.current_mode = "coc"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # 应用标题
        title = QLabel("🎲 角色卡")
        title.setObjectName("navTitle")
        layout.addWidget(title)

        # 模式按钮组
        self._mode_coc = QPushButton("🎭 COC (克苏鲁)")
        self._mode_coc.setObjectName("navButton")
        self._mode_coc.setCheckable(True)
        self._mode_coc.setChecked(True)
        self._mode_coc.clicked.connect(lambda: self._switch_mode("coc"))

        self._mode_dnd = QPushButton("🐉 DND (龙与地下城)")
        self._mode_dnd.setObjectName("navButton")
        self._mode_dnd.setCheckable(True)
        self._mode_dnd.clicked.connect(lambda: self._switch_mode("dnd"))

        layout.addWidget(self._mode_coc)
        layout.addWidget(self._mode_dnd)

        # 分隔线
        divider = QWidget()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        layout.addSpacing(12)
        layout.addWidget(divider)
        layout.addSpacing(8)

        # 功能按钮
        self._btn_settings = QPushButton("⚙️ 设置")
        self._btn_settings.setObjectName("navButton")
        self._btn_settings.clicked.connect(self.settings_requested.emit)

        self._btn_plugins = QPushButton("🔌 插件")
        self._btn_plugins.setObjectName("navButton")
        self._btn_plugins.clicked.connect(self._on_plugins)

        self._btn_history = QPushButton("📋 版本历史")
        self._btn_history.setObjectName("navButton")
        self._btn_history.clicked.connect(self._on_history)

        layout.addWidget(self._btn_settings)
        layout.addWidget(self._btn_plugins)
        layout.addWidget(self._btn_history)

        layout.addStretch()

        # 底部版本号
        ver = QLabel("v1.2.3")
        ver.setStyleSheet("color: rgba(255,255,255,0.25); font-size: 10px; padding: 8px 12px;")
        layout.addWidget(ver)

    def _on_history(self):
        """显示版本历史"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle("📋 版本历史")
        dlg.setMinimumSize(560, 480)
        dlg.setObjectName("detailWindow")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 16, 20, 16)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setHtml("""
<h2>📋 角色卡管理器 版本历史</h2>
<hr>
<h3 style="color: #6c63ff;">v1.2.3</h3>
<ul>
<li>🐛 <b>修复AI跑团插件</b>：设置在保存后未被插件重新读取的问题</li>
<li>🔄 <b>角色创建向导重置</b>：创建角色后自动重置到初始状态，可连续创建</li>
<li>🐛 <b>修复兴趣技能点显示</b>：阶段二剩余点数越分配越多的bug</li>
</ul>
<h3 style="color: #6c63ff;">v1.2.1</h3>
<ul>
<li>🐛 <b>修复插件管理对话框</b>：禁用插件复选框变灰不可点击的问题</li>
<li>🐛 <b>修复启用插件</b>：勾选禁用插件后显示「未知错误」不加载的问题</li>
<li>🐛 <b>修复剧本中文引号</b>：scenarios/__init__.py 中 "奇观"/"特殊表演" 引起的 SyntaxError</li>
</ul>
<h3 style="color: #6c63ff;">v1.2.0</h3>
<ul>
<li>🔌 <b>插件管理对话框</b>：勾选启用/禁用插件，状态持久化</li>
<li>⚙️ <b>设置标签页</b>：分为「外观」和「插件」两个标签页</li>
<li>🤖 <b>AI 跑团设置</b>：API Key 和模型选择存入设置</li>
<li>📖 <b>剧本扩充</b>：COC×10 + DND×10 共 20 个模组</li>
<li>📋 <b>版本历史</b>：本页面</li>
<li>🐛 修复角色选择确认按钮、插件加载错误提示等</li>
</ul>
<hr>
<h3 style="color: #6c63ff;">v1.1.2</h3>
<ul>
<li>🤖 <b>AI 跑团插件</b>：DeepSeek AI 主持跑团</li>
<li>🎲 手动掷骰面板 + 角色状态自动更新</li>
<li>📖 内置剧本 + 消除外部依赖</li>
</ul>
<hr>
<h3 style="color: #6c63ff;">v1.1.0</h3>
<ul>
<li>📤 导出功能 + ⚙️ 设置对话框</li>
<li>🎨 四套 UI 主题 + 深色标题栏</li>
<li>✨ 角色创建向导插件</li>
</ul>
<hr>
<h3 style="color: #6c63ff;">v1.0.0</h3>
<ul>
<li>🎲 COC 7th + DND 5e 双模式角色卡管理</li>
<li>🃏 磨砂玻璃卡片展示 + 📥 智能文本导入</li>
<li>🔍 多维搜索排序 + 🔌 插件系统</li>
<li>🗄️ SQLite 本地存储</li>
</ul>
""")
        layout.addWidget(te)
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("actionButton")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.exec()

    def _switch_mode(self, mode):
        """切换模式"""
        if mode == self.current_mode:
            return
        self.current_mode = mode
        self._mode_coc.setChecked(mode == "coc")
        self._mode_dnd.setChecked(mode == "dnd")
        self.mode_changed.emit(mode)

    def _on_plugins(self):
        """打开插件管理对话框"""
        from .plugin_manager_dialog import PluginManagerDialog
        parent = self.window()
        if hasattr(parent, 'plugin_manager'):
            dialog = PluginManagerDialog(parent.plugin_manager, self)
            dialog.exec()
