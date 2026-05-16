"""
AI 跑团游戏界面 — 角色选择、聊天、掷骰、状态监控
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
    QDialog, QGroupBox, QScrollArea, QMessageBox,
    QSplitter, QInputDialog, QAbstractItemView,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
import json
import threading

from .ai_keeper import (
    GameSession, call_deepseek, build_messages,
    parse_dice_request, update_character_from_ai,
)
from .scenarios import get_scenarios


# ==================== 角色选择对话框 ====================

class RoleSelectionDialog(QDialog):
    """两步选人对话框: ①勾选角色 → ②选玩家角色"""

    def __init__(self, mode, repository, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.repo = repository
        self.selected_characters = []
        self.player_character = None

        self.setWindowTitle("🎭 选择角色")
        self.setMinimumSize(500, 420)
        self.setModal(True)
        self.setObjectName("detailWindow")

        self._current_step = 0
        self._setup_ui()
        self._load_characters()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        self._title = QLabel("📋 第一步: 选择本次冒险的队伍成员")
        self._title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self._title)

        self._desc = QLabel("勾选要加入本次冒险的角色（至少选1个，可多选）")
        self._desc.setStyleSheet("color: rgba(255,255,255,0.6);")
        layout.addWidget(self._desc)

        self._char_list = QListWidget()
        self._char_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self._char_list, stretch=1)

        self._count_label = QLabel("已选: 0 个角色")
        self._count_label.setStyleSheet("color: rgba(255,255,255,0.5);")
        layout.addWidget(self._count_label)

        btn_layout = QHBoxLayout()
        skip_btn = QPushButton("自动组队 (全选)")
        skip_btn.setObjectName("sortButton")
        skip_btn.clicked.connect(self._select_all)
        btn_layout.addWidget(skip_btn)
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("sortButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self._next_btn = QPushButton("下一步 →")
        self._next_btn.setObjectName("actionButton")
        self._next_btn.clicked.connect(self._go_next)
        btn_layout.addWidget(self._next_btn)
        layout.addLayout(btn_layout)

    def _load_characters(self):
        """加载角色列表"""
        self._all_chars = self.repo.get_all(self.mode)
        self._char_list.clear()
        self._item_to_char = {}
        for char in self._all_chars:
            summary = char.get_card_summary()
            text = f"{summary['name']}  |  {summary['subtitle']}"
            if self.mode == "coc":
                hp = getattr(char, 'hp', '?')
                san = getattr(char, 'san', '?')
                text += f"   (HP:{hp} SAN:{san})"
            else:
                hp_c = getattr(char, 'hp_current', '?')
                hp_m = getattr(char, 'hp_max', '?')
                text += f"   (HP:{hp_c}/{hp_m})"
            item = QListWidgetItem(text)
            self._char_list.addItem(item)
            self._item_to_char[text] = char

        self._char_list.itemSelectionChanged.connect(self._update_count)

    def _update_count(self):
        count = len(self._char_list.selectedItems())
        self._count_label.setText(f"已选: {count} 个角色")

    def _select_all(self):
        self._char_list.selectAll()

    def _go_next(self):
        """进入第二步: 选择玩家扮演的角色"""
        selected = [self._item_to_char[item.text()]
                    for item in self._char_list.selectedItems()
                    if item.text() in self._item_to_char]

        if not selected:
            QMessageBox.warning(self, "提示", "请至少选择1个角色！")
            return

        if self._current_step == 0:
            # 进入第2步
            self.selected_characters = selected
            self._current_step = 1
            self._title.setText("🎭 第二步: 选择你扮演的角色")
            self._desc.setText("在下方的角色中选择一个作为你的角色，其余会由 AI 扮演。")
        elif self._current_step == 1:
            # 确认选择，完成
            items = self._char_list.selectedItems()
            if items:
                self.player_character = self._item_to_char[items[0].text()]
                self.accept()
            else:
                QMessageBox.warning(self, "提示", "请选择你要扮演的角色！")

            # 清空并重建列表为单选模式
            self._char_list.clear()
            self._char_list.setSelectionMode(QAbstractItemView.SingleSelection)
            self._char_list.itemSelectionChanged.disconnect()
            for char in selected:
                summary = char.get_card_summary()
                text = f"🎮 {summary['name']}  |  {summary['subtitle']}"
                item = QListWidgetItem(text)
                self._char_list.addItem(item)
                self._item_to_char[text] = char

            self._count_label.setText("选择你要扮演的角色")
            self._next_btn.setText("✅ 确认开始冒险")
            self._char_list.itemSelectionChanged.connect(self._update_player_selection)

    def _update_player_selection(self):
        items = self._char_list.selectedItems()
        if items:
            char = self._item_to_char[items[0].text()]
            self._desc.setText(f"你选择了「{char.name}」作为你的角色，其余角色由 AI 操控。")
            self._count_label.setText(f"玩家: {char.name}  |  AI操控: {len(self.selected_characters)-1} 个队友")

    def get_result(self):
        items = self._char_list.selectedItems()
        if items:
            self.player_character = self._item_to_char[items[0].text()]
        return self.selected_characters, self.player_character


# ==================== 剧本选择对话框 ====================

class ScenarioSelectionDialog(QDialog):
    """剧本选择对话框"""

    def __init__(self, mode, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.selected_scenario = None

        self.setWindowTitle("📖 选择剧本")
        self.setMinimumSize(550, 380)
        self.setModal(True)
        self.setObjectName("detailWindow")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("📖 选择冒险剧本")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("选择一个预置剧本，或让 AI 即兴创作：")
        desc.setStyleSheet("color: rgba(255,255,255,0.6);")
        layout.addWidget(desc)

        self._scenario_list = QListWidget()
        scenarios = get_scenarios(mode)

        # 预置剧本
        for s in scenarios:
            item = QListWidgetItem(f"📜 {s['title']}\n   {s['summary'][:60]}…")
            item.setData(Qt.UserRole, s)
            self._scenario_list.addItem(item)

        # AI 生成选项
        ai_item = QListWidgetItem("🤖 让 AI 即兴创作 — 根据你的偏好现场生成")
        ai_item.setData(Qt.UserRole, None)
        self._scenario_list.addItem(ai_item)

        custom_item = QListWidgetItem("✏️ 自定义剧情 — 输入你自己的故事梗概")
        custom_item.setData(Qt.UserRole, "custom")
        self._scenario_list.addItem(custom_item)

        layout.addWidget(self._scenario_list)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("sortButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        start_btn = QPushButton("✅ 开始冒险")
        start_btn.setObjectName("actionButton")
        start_btn.clicked.connect(self._confirm)
        btn_layout.addWidget(start_btn)
        layout.addLayout(btn_layout)

    def _confirm(self):
        items = self._scenario_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "提示", "请选择一个剧本！")
            return

        data = items[0].data(Qt.UserRole)
        if data == "custom":
            # 让用户输入自定义剧情
            text, ok = QInputDialog.getMultiLineText(
                self, "自定义剧情", "输入你的故事梗概或剧本描述:"
            )
            if ok and text.strip():
                self.selected_scenario = {
                    "id": "custom",
                    "title": "自定义剧情",
                    "intro": text.strip(),
                    "type": self.mode,
                }
                self.accept()
        elif data is None:
            # AI 即兴创作
            text, ok = QInputDialog.getMultiLineText(
                self, "AI 创作提示",
                "告诉 AI 你想跑什么风格的冒险\n"
                "(如: 1920年代的神秘谋杀 / 地牢探险 / 深海恐惧):"
            )
            if ok:
                pref = text.strip() or "标准冒险"
                self.selected_scenario = {
                    "id": "ai_generated",
                    "title": f"AI 生成: {pref[:30]}",
                    "intro": f"请根据以下偏好即兴创作一个冒险: {pref}",
                    "type": self.mode,
                }
                self.accept()
        else:
            self.selected_scenario = data
            self.accept()


# ==================== AI 跑团聊天界面 ====================

class AIKeeperUI(QWidget):
    """AI 跑团主界面 — 聊天 + 掷骰 + 状态"""

    ai_response_ready = Signal(object)  # 后台线程安全地传回 AI 回复 (dict)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.session = GameSession()

        # 从设置中加载 API Key 和模型
        import json
        from pathlib import Path
        from character_manager.paths import load_settings_json
        saved = load_settings_json()
        self.api_key = saved.get("ai_keeper_api_key", "")
        self.model = saved.get("ai_keeper_model", "deepseek-v4-flash")

        self._waiting_for_ai = False
        self.ai_response_ready.connect(self._handle_ai_response)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # ===== 顶部状态栏 =====
        self._status_bar = QWidget()
        self._status_bar.setStyleSheet("background: rgba(255,255,255,0.04);")
        status_layout = QHBoxLayout(self._status_bar)
        status_layout.setContentsMargins(16, 8, 16, 8)

        self._status_label = QLabel("🏁 尚未开始游戏 — 点击「开始冒险」部署角色")
        self._status_label.setStyleSheet("font-weight: 500;")

        self._start_btn = QPushButton("🎲 开始冒险")
        self._start_btn.setObjectName("actionButton")
        self._start_btn.clicked.connect(self._start_game)

        status_layout.addWidget(self._status_label, stretch=1)
        status_layout.addWidget(self._start_btn)
        layout.addWidget(self._status_bar)

        # ===== 主内容区 =====
        splitter = QSplitter(Qt.Horizontal)

        # -- 左侧: 聊天区 --
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(12, 8, 6, 8)

        self._chat_title = QLabel("💬 冒险日志")
        self._chat_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        chat_layout.addWidget(self._chat_title)

        self._chat_display = QTextEdit()
        self._chat_display.setReadOnly(True)
        self._chat_display.setStyleSheet("""
            background: rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 12px;
            font-size: 14px;
            line-height: 1.6;
        """)
        chat_layout.addWidget(self._chat_display, stretch=1)

        # 输入区
        input_row = QHBoxLayout()
        self._chat_input = QLineEdit()
        self._chat_input.setPlaceholderText("输入你的行动或对话… (Enter 发送)")
        self._chat_input.returnPressed.connect(self._send_message)
        self._chat_input.setEnabled(False)

        self._send_btn = QPushButton("发送")
        self._send_btn.setObjectName("actionButton")
        self._send_btn.clicked.connect(self._send_message)
        self._send_btn.setEnabled(False)

        input_row.addWidget(self._chat_input, stretch=1)
        input_row.addWidget(self._send_btn)
        chat_layout.addLayout(input_row)

        splitter.addWidget(chat_panel)

        # -- 右侧: 状态面板 --
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(6, 8, 12, 8)
        right_layout.setSpacing(8)

        # 骰子面板
        dice_group = QGroupBox("🎲 掷骰")
        dice_layout = QVBoxLayout(dice_group)
        dice_layout.setSpacing(6)

        dice_label = QLabel("AI 要求检定时点击对应的骰子:")
        dice_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.5);")
        dice_layout.addWidget(dice_label)

        dice_btn_row1 = QHBoxLayout()
        for name, sides in [("D100", 100), ("D20", 20), ("D12", 12)]:
            btn = QPushButton(name)
            btn.setObjectName("sortButton")
            btn.clicked.connect(lambda checked, s=sides, n=name: self._roll_dice(s, n))
            btn.setEnabled(False)
            dice_btn_row1.addWidget(btn)
        dice_layout.addLayout(dice_btn_row1)

        dice_btn_row2 = QHBoxLayout()
        for name, sides in [("D10", 10), ("D8", 8), ("D6", 6), ("D4", 4)]:
            btn = QPushButton(name)
            btn.setObjectName("sortButton")
            btn.clicked.connect(lambda checked, s=sides, n=name: self._roll_dice(s, n))
            btn.setEnabled(False)
            dice_btn_row2.addWidget(btn)
        dice_layout.addLayout(dice_btn_row2)

        # 自定义掷骰
        custom_row = QHBoxLayout()
        self._custom_dice_input = QLineEdit()
        self._custom_dice_input.setPlaceholderText("3d6")
        self._custom_dice_input.setEnabled(False)
        custom_dice_btn = QPushButton("掷!")
        custom_dice_btn.setObjectName("actionButton")
        custom_dice_btn.setFixedWidth(50)
        custom_dice_btn.clicked.connect(lambda: self._roll_custom_dice())
        custom_dice_btn.setEnabled(False)
        custom_row.addWidget(self._custom_dice_input)
        custom_row.addWidget(custom_dice_btn)
        dice_layout.addLayout(custom_row)

        self._last_roll_label = QLabel("上次掷骰: —")
        self._last_roll_label.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 12px;")
        dice_layout.addWidget(self._last_roll_label)

        right_layout.addWidget(dice_group)

        # 角色状态
        status_group = QGroupBox("📊 角色状态")
        self._status_display = QTextEdit()
        self._status_display.setReadOnly(True)
        self._status_display.setMaximumHeight(180)
        self._status_display.setStyleSheet("""
            background: rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            padding: 8px;
            font-size: 12px;
        """)
        self._status_display.setPlaceholderText("开始游戏后显示角色状态…")
        status_group.setLayout(QVBoxLayout())
        status_group.layout().addWidget(self._status_display)
        right_layout.addWidget(status_group)

        # API Key 设置
        ak_label = "✅ API Key 已设置" if self.api_key else "🔑 设置 API Key"
        self._api_btn = QPushButton(ak_label)
        self._api_btn.setObjectName("sortButton")
        self._api_btn.clicked.connect(self._set_api_key)
        right_layout.addWidget(self._api_btn)

        right_layout.addStretch()
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 280])

        layout.addWidget(splitter, stretch=1)

        # 底部状态栏：显示模型和 token 用量
        self._status_bar_label = QLabel("准备就绪")
        self._status_bar_label.setStyleSheet(
            "color: rgba(255,255,255,0.3); font-size: 11px; padding: 4px 12px;"
        )
        layout.addWidget(self._status_bar_label)

        self._dice_btns = []

    def _set_api_key(self):
        """设置 API Key"""
        key, ok = QInputDialog.getText(
            self, "DeepSeek API Key",
            "请输入你的 DeepSeek API Key\n(在 platform.deepseek.com 获取):",
            text=self.api_key,
        )
        if ok and key.strip():
            self.api_key = key.strip()
            self.session.api_key = key.strip()
            self._api_btn.setText("✅ API Key 已设置")
            QMessageBox.information(self, "已保存", "API Key 设置成功！\n重新开始冒险即可使用。")

    def _start_game(self):
        """开始游戏 — 选角色 → 选剧本 → 启动"""
        # 重新读取设置（用户可能在设置界面更新了 API Key）
        from character_manager.paths import load_settings_json
        saved = load_settings_json()
        self.api_key = saved.get("ai_keeper_api_key", "") or self.api_key
        self.model = saved.get("ai_keeper_model", "deepseek-v4-flash") or self.model
        self._api_btn.setText("✅ API Key 已设置" if self.api_key else "🔑 设置 API Key")

        if not self.api_key:
            reply = QMessageBox.question(
                self, "需要 API Key",
                "尚未设置 DeepSeek API Key。\n\n"
                "你可以现在输入，或前往\n「设置 → 插件」标签页中保存。",
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                self._set_api_key()
            if not self.api_key:
                return

        if not self.main_window:
            return

        mode = getattr(self.main_window, 'current_mode', 'coc')
        repo = getattr(self.main_window, 'repository', None)
        if not repo:
            QMessageBox.warning(self, "错误", "无法访问角色数据！")
            return

        # 第一步: 选角色
        role_dialog = RoleSelectionDialog(mode, repo, self)
        if not role_dialog.exec():
            return
        all_chars, player_char = role_dialog.get_result()
        if not all_chars or not player_char:
            return

        # 第二步: 选剧本
        scene_dialog = ScenarioSelectionDialog(mode, self)
        if not scene_dialog.exec():
            return
        scenario = scene_dialog.selected_scenario

        # 初始化游戏会话
        self.session = GameSession()
        self.session.mode = mode
        self.session.api_key = self.api_key
        self.session.init_characters(all_chars, player_char)
        self.session.scenario = scenario
        self.session.conversation_history = []
        self.session.turn_count = 0

        # 更新 UI
        self._chat_input.setEnabled(True)
        self._send_btn.setEnabled(True)
        self._api_btn.setText("✅ API Key 已设置")
        self._start_btn.setText("🔄 重新开始")
        self._status_label.setText(
            f"🎭 正在冒险 | "
            f"玩家: {player_char.name} | "
            f"队伍: {len(all_chars)}人 | "
            f"{scenario.get('title', '即兴创作')}"
        )

        # 启用骰子按钮
        for layout_item in self.findChildren(QGroupBox):
            for btn in layout_item.findChildren(QPushButton):
                if btn.text() in ["D100", "D20", "D12", "D10", "D8", "D6", "D4", "掷!"]:
                    btn.setEnabled(True)
        self._custom_dice_input.setEnabled(True)

        # 清空聊天
        self._chat_display.clear()
        self._add_system_message(f"🎭 冒险开始！")
        self._add_system_message(f"你扮演: {player_char.name}")
        self._add_system_message(f"队友: {', '.join(c.name for c in self.session.npc_characters)}")
        self._add_system_message(f"剧本: {scenario.get('title', '即兴创作')}")
        self._add_system_message("")

        # 更新状态显示
        self._update_status_display()

        # AI 开场白
        intro = scenario.get('intro', '冒险开始了…')
        ai_prompt = f"开场: 请用生动的描述开始这场冒险。\n{intro}\n\n队伍配置:\n{self.session.get_character_summary()}"
        self._ai_say(ai_prompt)

    def _add_system_message(self, text):
        """添加系统消息到聊天"""
        self._chat_display.append(f"<span style='color: rgba(255,255,255,0.5); font-style: italic;'>{text}</span>")

    def _add_player_message(self, text):
        """添加玩家消息"""
        name = self.session.player_character.name if self.session.player_character else "玩家"
        self._chat_display.append(f"<br><b style='color: #6c63ff;'>{name}:</b> {text}")

    def _add_ai_message(self, text):
        """添加 AI 消息"""
        text = text.replace("\n", "<br>")
        self._chat_display.append(f"<br><b style='color: #3dd68c;'>🎲 Keeper:</b><br>{text}")

    def _send_message(self):
        """发送玩家消息"""
        if self._waiting_for_ai:
            return

        text = self._chat_input.text().strip()
        if not text:
            return
        self._chat_input.clear()

        self._add_player_message(text)
        self._add_system_message("⏳ Keeper 正在思考…")

        self._waiting_for_ai = True
        self._chat_input.setEnabled(False)
        self._send_btn.setEnabled(False)

        # 后台线程调用 API
        thread = threading.Thread(target=self._ai_response, args=(text,))
        thread.daemon = True
        thread.start()

    def _ai_response(self, player_input):
        """AI 回应（后台线程）"""
        # 构建消息
        messages = build_messages(self.session, player_input)

        # 保存用户消息到历史
        if player_input:
            self.session.conversation_history.append({
                "role": "user", "content": player_input
            })

        # 调用 API
        response = call_deepseek(self.api_key, messages, model=self.model)

        # 通过信号安全地回到主线程更新 UI
        self.ai_response_ready.emit(response)

    def _handle_ai_response(self, result):
        """处理 AI 回应（主线程）"""
        self._waiting_for_ai = False
        self._chat_input.setEnabled(True)
        self._send_btn.setEnabled(True)

        # 从返回的 dict 中提取信息
        if isinstance(result, dict):
            content = result.get("content", str(result))
            model_name = result.get("model", self.model)
            usage = result.get("usage", {})
            pt = usage.get("prompt_tokens", 0)
            ct = usage.get("completion_tokens", 0)
            tt = usage.get("total_tokens", 0)

            # 更新底部状态栏（显示实际调用的模型名）
            model_short = "flash" if "flash" in model_name else "pro" if "pro" in model_name else model_name
            if tt > 0:
                self._status_bar_label.setText(
                    f"🤖 {model_short}  |  本次: 输入 {pt} + 输出 {ct} = {tt} tokens"
                )
        else:
            content = str(result)

        # 添加 AI 回复
        self._add_ai_message(content)

        # 检查是否需要掷骰
        dice_request = parse_dice_request(content)
        if dice_request:
            self._add_system_message(
                f"🎲 Keeper 要求进行「{dice_request}」检定，请点击右侧骰子掷骰！"
            )
            self._last_roll_label.setText(f"🎲 需要检定: {dice_request}")

        # 保存 AI 回复到历史
        self.session.conversation_history.append({
            "role": "assistant", "content": content
        })
        self.session.turn_count += 1

        # 更新角色状态
        updates = update_character_from_ai(self.session, content)
        if updates:
            self._add_system_message(f"📊 角色状态更新: {'; '.join(updates)}")
            self._update_status_display()

        # 滚动到底部
        scrollbar = self._chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _roll_dice(self, sides, name):
        """掷骰子（指定面数）"""
        if self._waiting_for_ai:
            return
        import random
        result = random.randint(1, sides)
        self._last_roll_label.setText(f"🎲 {name}: {result}")

        # 发送结果到聊天
        char_name = self.session.player_character.name if self.session.player_character else "玩家"
        self._add_player_message(f"[掷出 {name}: **{result}**]")

        # 自动发送给 AI
        check_name = self._last_roll_label.text()
        self._chat_input.setText(f"[检定结果: {name} 掷出 {result}]")
        self._send_message()

    def _roll_custom_dice(self):
        """自定义掷骰"""
        dice_str = self._custom_dice_input.text().strip()
        if not dice_str or self._waiting_for_ai:
            return

        import re, random
        m = re.match(r"(\d+)?d(\d+)([+-]\d+)?", dice_str.lower().replace(" ", ""))
        if not m:
            self._add_system_message("⚠️ 格式错误，请使用如 2d6、1d20、3d6+2 的格式")
            return

        count = int(m.group(1)) if m.group(1) else 1
        sides = int(m.group(2))
        mod = int(m.group(3)) if m.group(3) else 0
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results) + mod

        result_str = f"{' + '.join(map(str, results))}"
        if mod:
            result_str += f" + {mod}"
        result_str += f" = {total}"

        self._last_roll_label.setText(f"🎲 {dice_str}: {total}")
        self._add_player_message(f"[掷出 {dice_str}: **{result_str}**]")

        self._chat_input.setText(f"[检定结果: {dice_str} → {total} ({', '.join(map(str, results))})]")
        self._send_message()

    def _update_status_display(self):
        """更新角色状态显示"""
        if not self.session.player_character:
            return

        char = self.session.player_character
        lines = []
        lines.append(f"🎮 {char.name}")
        if hasattr(char, 'hp'):
            lines.append(f"HP: {getattr(char, 'hp', '?')}")
            lines.append(f"SAN: {getattr(char, 'san', '?')}")
            lines.append(f"MP: {getattr(char, 'mp', '?')}")
            lines.append(f"幸运: {getattr(char, 'luck', '?')}")
        else:
            lines.append(f"HP: {getattr(char, 'hp_current', '?')}/{getattr(char, 'hp_max', '?')}")
            lines.append(f"AC: {getattr(char, 'armor_class', '?')}")

        lines.append(f"\n队友:")
        for c in self.session.npc_characters:
            lines.append(f"  {c.name}")

        self._status_display.setPlainText("\n".join(lines))
