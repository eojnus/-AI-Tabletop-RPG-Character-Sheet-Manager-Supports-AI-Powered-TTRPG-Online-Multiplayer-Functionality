"""
AI Keeper 跑团助手插件 — DeepSeek 驱动的 TRPG 主持人
"""
from character_manager.plugin.plugin_base import PluginBase
from .game_ui import AIKeeperUI


class AIKeeperPlugin(PluginBase):
    """AI Keeper / DM 跑团助手"""

    PLUGIN_NAME = "🤖 AI 跑团助手"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "使用 DeepSeek AI 作为跑团主持人(Keeper/DM)，支持 COC 7th 和 DND 5e"

    def on_ui_ready(self, main_window):
        """添加跑团助手标签页"""
        self.keeper_ui = AIKeeperUI(main_window=main_window)
        main_window.add_plugin_tab("ai_keeper", "🤖 AI 跑团", self.keeper_ui)
