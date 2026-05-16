"""
网络桥接插件 — P2P 联机 + 联网接入
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QGroupBox, QMessageBox, QInputDialog,
)
from PySide6.QtCore import Qt

from character_manager.plugin.plugin_base import PluginBase


class NetworkBridgePlugin(PluginBase):
    """网络桥接插件"""

    PLUGIN_NAME = "🌐 网络联机"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "P2P 联机组队 + 互联网接入服务"

    def __init__(self):
        super().__init__()
        self.server = None
        self.client = None
        self.web = None

    def on_ui_ready(self, main_window):
        """注册标签页"""
        self.network_ui = NetworkPanel(main_window, self)
        main_window.add_plugin_tab("network_bridge", "🌐 联机", self.network_ui)

    def get_web_access(self):
        """其他插件获取网络接入实例"""
        if not self.web:
            from .web_access import WebAccess
            self.web = WebAccess()
        return self.web

    def get_server(self):
        return self.server

    def get_client(self):
        return self.client

    def get_settings_widget(self):
        """设置界面（在设置 > 插件中显示）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "🌐 网络联机插件设置\n\n"
            "联机需要安装 websockets 库:\n"
            "pip install websockets\n\n"
            "依赖状态: " + (
                "✅ websockets 已安装" if _websockets_available() else "❌ websockets 未安装"
            )
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        btn = QPushButton("检测依赖")
        btn.clicked.connect(lambda: QMessageBox.information(
            widget, "依赖状态",
            "websockets 库: " + ("✅ 已安装" if _websockets_available() else "❌ 未安装")
        ))
        layout.addWidget(btn)
        layout.addStretch()

        return widget


def _websockets_available():
    try:
        import websockets
        return True
    except ImportError:
        return False


# ==================== 网络控制面板 ====================

class NetworkPanel(QWidget):
    """网络联机控制面板（嵌入标签页）"""

    def __init__(self, main_window, plugin):
        super().__init__()
        self.main_window = main_window
        self.plugin = plugin
        self.server = None
        self.client = None
        self._nickname = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("🌐 网络联机组队")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # 昵称设置
        nick_row = QHBoxLayout()
        nick_row.addWidget(QLabel("你的昵称:"))
        self._nick_input = QLineEdit()
        self._nick_input.setPlaceholderText("输入昵称（可选）")
        self._nick_input.setMaxLength(12)
        self._nick_input.textChanged.connect(lambda t: setattr(self, '_nickname', t or ''))
        nick_row.addWidget(self._nick_input, stretch=1)
        layout.addLayout(nick_row)

        # ===== 模式选择/服务器状态（共享区域）=====
        self._mode_group = QGroupBox("选择模式")
        self._mode_layout = QHBoxLayout(self._mode_group)
        self._mode_layout.setSpacing(20)

        self._host_btn = QPushButton("🎮 主持游戏\n（开启服务器）")
        self._host_btn.setMinimumSize(180, 80)
        self._host_btn.setStyleSheet(
            "QPushButton { background: rgba(108,99,255,0.15); border: 2px solid rgba(108,99,255,0.3); "
            "border-radius: 12px; font-size: 14px; }"
            "QPushButton:hover { background: rgba(108,99,255,0.25); }"
        )
        self._host_btn.clicked.connect(self._host_game)
        self._mode_layout.addWidget(self._host_btn)

        self._join_btn = QPushButton("🔗 加入游戏\n（连接房主）")
        self._join_btn.setMinimumSize(180, 80)
        self._join_btn.setStyleSheet(
            "QPushButton { background: rgba(61,214,140,0.15); border: 2px solid rgba(61,214,140,0.3); "
            "border-radius: 12px; font-size: 14px; }"
            "QPushButton:hover { background: rgba(61,214,140,0.25); }"
        )
        self._join_btn.clicked.connect(self._join_game)
        self._mode_layout.addWidget(self._join_btn)

        # 服务器信息面板（主持后显示）
        self._server_info = QWidget()
        self._server_info.setVisible(False)
        si_layout = QVBoxLayout(self._server_info)
        si_layout.setSpacing(8)

        self._server_ip_label = QLabel()
        self._server_ip_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #6c63ff; padding: 8px;"
            "background: rgba(108,99,255,0.08); border-radius: 8px;"
        )
        self._server_ip_label.setAlignment(Qt.AlignCenter)
        si_layout.addWidget(self._server_ip_label)

        self._server_status_label = QLabel()
        self._server_status_label.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.6);")
        self._server_status_label.setAlignment(Qt.AlignCenter)
        si_layout.addWidget(self._server_status_label)

        self._stop_server_btn = QPushButton("⏹️ 停止服务器")
        self._stop_server_btn.setObjectName("dangerButton")
        self._stop_server_btn.clicked.connect(self._stop_server)
        si_layout.addWidget(self._stop_server_btn, alignment=Qt.AlignCenter)

        self._mode_layout.addWidget(self._server_info)

        layout.addWidget(self._mode_group)

        # ===== 房间状态 =====
        status_group = QGroupBox("📊 房间状态")
        status_layout = QVBoxLayout(status_group)

        self._status_label = QLabel("当前未连接任何房间")
        self._status_label.setStyleSheet("font-size: 14px;")
        status_layout.addWidget(self._status_label)

        # 快捷语
        quick_label = QLabel("💬 快捷语:")
        quick_label.setStyleSheet("font-weight: 500; margin-top: 8px;")
        status_layout.addWidget(quick_label)

        quick_grid = QHBoxLayout()
        from .protocol import QUICK_MESSAGES
        for emoji, text in QUICK_MESSAGES[:6]:
            btn = QPushButton(f"{emoji}")
            btn.setObjectName("sortButton")
            btn.setToolTip(text)
            btn.clicked.connect(lambda checked, t=text: self._send_quick_msg(t))
            quick_grid.addWidget(btn)
        status_layout.addLayout(quick_grid)

        status_layout.addWidget(QLabel("更多快捷语（第2行）:"))
        quick_grid2 = QHBoxLayout()
        for emoji, text in QUICK_MESSAGES[6:]:
            btn = QPushButton(f"{emoji}")
            btn.setObjectName("sortButton")
            btn.setToolTip(text)
            btn.clicked.connect(lambda checked, t=text: self._send_quick_msg(t))
            quick_grid2.addWidget(btn)
        status_layout.addLayout(quick_grid2)

        # 在线玩家
        status_layout.addWidget(QLabel("👥 在线玩家:"))
        self._player_list = QListWidget()
        self._player_list.setMaximumHeight(120)
        status_layout.addWidget(self._player_list)

        layout.addWidget(status_group)

        # ===== 聊天区 =====
        chat_group = QGroupBox("💬 聊天")
        chat_layout = QVBoxLayout(chat_group)
        self._chat_display = QLabel("聊天记录将显示在这里…")
        self._chat_display.setWordWrap(True)
        self._chat_display.setStyleSheet(
            "background: rgba(0,0,0,0.15); border-radius: 8px; padding: 8px;"
        )
        chat_layout.addWidget(self._chat_display)

        chat_input_row = QHBoxLayout()
        self._chat_input = QLineEdit()
        self._chat_input.setPlaceholderText("输入聊天消息…")
        self._chat_input.returnPressed.connect(self._send_chat)
        chat_btn = QPushButton("发送")
        chat_btn.setObjectName("actionButton")
        chat_btn.clicked.connect(self._send_chat)
        chat_input_row.addWidget(self._chat_input, stretch=1)
        chat_input_row.addWidget(chat_btn)
        chat_layout.addLayout(chat_input_row)

        layout.addWidget(chat_group, stretch=1)

    def _get_nick(self):
        return self._nickname.strip() or "匿名"

    # ==================== 主持游戏 ====================

    def _host_game(self):
        if self.client and self.client.connected:
            QMessageBox.information(self, "提示", "你已在游戏中，请先断开当前连接。")
            return

        # 先检查 websockets 是否可用
        from . import _websockets_available
        if not _websockets_available():
            QMessageBox.critical(self, "缺少依赖",
                "需要安装 websockets 库才能开启服务器。\n\n"
                "请在终端运行: pip install websockets"
            )
            return

        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        from .server import GameServer
        self.server = GameServer(port=9876)
        try:
            self.server.start()

            # 隐藏选择按钮，显示服务器信息
            self._host_btn.setVisible(False)
            self._join_btn.setVisible(False)
            self._server_info.setVisible(True)
            self._mode_group.setTitle("🎮 服务器运行中")

            self._server_ip_label.setText(
                f"📋 {local_ip}:9876\n"
                f"把此地址发给你的队友"
            )
            self._server_status_label.setText("等待玩家加入… 已连接: 0 人")
            self._status_label.setText(f"✅ 房间已创建 | IP: {local_ip}:9876")

            # 注册事件
            self.server.on("join", lambda data: self._on_player_change())
            self.server.on("leave", lambda data: self._on_player_change())

        except Exception as e:
            self._server_info.setVisible(False)
            self._host_btn.setVisible(True)
            self._join_btn.setVisible(True)
            QMessageBox.critical(self, "创建失败",
                f"无法创建房间:\n{str(e)}\n\n"
                "可能原因:\n"
                "• websockets 未安装 (pip install websockets)\n"
                "• 端口 9876 被占用\n"
                "• 防火墙阻止"
            )

    def _stop_server(self):
        """停止服务器"""
        if self.server:
            self.server.stop()
            self.server = None
        self._server_info.setVisible(False)
        self._host_btn.setVisible(True)
        self._join_btn.setVisible(True)
        self._mode_group.setTitle("选择模式")
        self._status_label.setText("服务器已停止")
        self._player_list.clear()

    def _on_player_change(self):
        if self.server:
            count = self.server.get_player_count()
            self._status_label.setText(
                f"✅ 房间运行中 | IP: {self.server.host}:{self.server.port}\n"
                f"👥 已连接: {count} 人"
            )
            self._server_status_label.setText(f"已连接: {count} 人")
            self._update_player_list()

    def _update_player_list(self):
        self._player_list.clear()
        if self.server:
            for p in self.server._player_list():
                self._player_list.addItem(f"🟢 {p['nick']}")

    # ==================== 加入游戏 ====================

    def _join_game(self):
        ip, ok = QInputDialog.getText(
            self, "加入游戏",
            "输入房主的 IP 地址（含端口，如 192.168.1.100:9876）:",
        )
        if not ok or not ip.strip():
            return

        if ":" in ip:
            host, port = ip.rsplit(":", 1)
            try:
                port = int(port)
            except ValueError:
                port = 9876
        else:
            host, port = ip, 9876

        from .client import GameClient
        self.client = GameClient()
        self.client.on("connected", lambda data: self._on_connected(data))
        self.client.on("player_list", lambda data: self._update_remote_players(data))
        self.client.on("chat", lambda data: self._on_remote_chat(data))

        try:
            self.client.connect(host, port, nick=self._get_nick())
            self._status_label.setText(f"🔄 正在连接 {host}:{port}…")
        except Exception as e:
            QMessageBox.critical(self, "连接失败", str(e))

    def _on_connected(self, data):
        self._status_label.setText("✅ 已加入房间！")
        self._player_list.addItem(f"🟢 你 (自己)")

    def _update_remote_players(self, players):
        self._player_list.clear()
        for p in players:
            dot = "🟢" if p.get("online") else "⚫"
            self._player_list.addItem(f"{dot} {p['nick']}")

    # ==================== 聊天 ====================

    def _send_chat(self):
        text = self._chat_input.text().strip()
        if not text:
            return
        self._chat_input.clear()
        nick = self._get_nick()

        if self.server:
            # 房主：显示到本地并广播
            self._chat_display.setText(f"<b>{nick}:</b> {text}")
            for cb in self.server._callbacks.get("chat", []):
                cb({"player": nick, "text": text})
        elif self.client and self.client.connected:
            self.client.send_chat(text)

    def _send_quick_msg(self, text):
        """发送快捷语"""
        nick = self._get_nick()
        if self.server:
            self._chat_display.setText(f"<b>{nick}:</b> {text}")
        elif self.client and self.client.connected:
            self.client.send_quick_msg(text)

    def _on_remote_chat(self, data):
        player = data.get("player", "未知")
        text = data.get("text", "")
        self._chat_display.setText(f"<b>{player}:</b> {text}")
