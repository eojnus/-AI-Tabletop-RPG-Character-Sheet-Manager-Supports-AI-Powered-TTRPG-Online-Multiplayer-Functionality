"""
角色创建向导插件 — 引导玩家按规则逐步创建 COC/DND 角色
"""
from character_manager.plugin.plugin_base import PluginBase
from .creator_wizard import CharacterCreatorWizard


class CharacterCreatorPlugin(PluginBase):
    """角色创建向导插件"""

    PLUGIN_NAME = "角色创建向导"
    PLUGIN_VERSION = "1.0.2"
    PLUGIN_DESCRIPTION = "引导玩家按规则逐步创建 COC 或 DND 角色，自动掷骰、分配技能、设置装备"

    def on_ui_ready(self, main_window):
        """在标签页中添加创建向导"""
        self.wizard = CharacterCreatorWizard(parent=main_window)
        main_window.add_plugin_tab("character_creator", "✨ 创建角色", self.wizard)
