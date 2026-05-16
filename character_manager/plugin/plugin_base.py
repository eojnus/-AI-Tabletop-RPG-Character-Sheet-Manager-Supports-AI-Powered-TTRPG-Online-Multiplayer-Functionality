"""
插件基类 — 所有插件必须继承此类
定义插件生命周期钩子和可覆写的方法
"""
import importlib
import inspect
import os


class PluginBase:
    """
    插件基类

    子类必须定义:
        PLUGIN_NAME: str  — 插件名称
        PLUGIN_VERSION: str — 插件版本
        PLUGIN_DESCRIPTION: str — 插件描述

    可选覆写的方法（按调用顺序排列）:
        1. on_load(app)           — 插件被加载时调用（此时UI可能还未就绪）
        2. on_ui_ready(window)    — 主窗口准备就绪，可以注入UI元素
        3. on_enable()            — 插件被启用时调用
        4. on_mode_switch(mode)   — 用户在COC/DND间切换时
        5. on_character_created(c) — 角色创建后
        6. on_character_updated(c) — 角色更新后
        7. on_character_deleted(c) — 角色删除前
        8. on_search(query, filters, results) — 搜索时（可修改结果）
        9. on_disable()           — 插件被禁用时调用
        10. on_unload()           — 插件被卸载时调用
    """

    # ======== 插件元信息（子类必须重写）========
    PLUGIN_NAME = "未命名插件"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = ""

    def __init__(self):
        self.app = None
        self.main_window = None
        self.enabled = True

    # ======== 生命周期钩子 ========

    def on_load(self, app):
        """
        插件加载时调用
        app: 应用实例，可通过 app 访问数据库等核心服务
        """
        pass

    def on_ui_ready(self, main_window):
        """
        主窗口就绪时调用
        main_window: 主窗口实例，可通过它添加菜单、工具栏、标签页等
        """
        pass

    def on_enable(self):
        """插件被启用时调用"""
        pass

    def on_disable(self):
        """插件被禁用时调用"""
        pass

    def on_unload(self):
        """插件被卸载时调用"""
        pass

    # ======== 业务钩子 ========

    def on_mode_switch(self, mode):
        """
        模式切换时调用
        mode: "coc" 或 "dnd"
        """
        pass

    def on_character_created(self, character):
        """
        角色创建后调用
        character: 新创建的角色对象（已有 ID）
        """
        pass

    def on_character_updated(self, character):
        """
        角色更新后调用
        character: 更新后的角色对象
        """
        pass

    def on_character_deleted(self, character):
        """
        角色删除前调用
        character: 即将被删除的角色对象
        """
        pass

    def on_search(self, query, filters, results):
        """
        搜索时调用（可修改搜索结果）
        参数:
            query: 搜索关键词
            filters: 过滤条件字典
            results: 当前搜索结果列表（可直接修改）

        返回: 修改后的结果列表，或 None
        """
        return results

    # ======== UI 注入辅助方法 ========

    def add_menu_item(self, menu_name, item_text, callback):
        """
        向指定菜单添加选项
        menu_name: 菜单名（如"插件"，不存在会创建）
        item_text: 菜单项文字
        callback: 点击时的回调函数
        """
        if not self.main_window:
            return
        self.main_window.add_plugin_menu_item(menu_name, item_text, callback)

    def add_toolbar_button(self, text, icon_path=None, callback=None):
        """
        向工具栏添加按钮
        """
        if not self.main_window:
            return
        self.main_window.add_plugin_toolbar_button(text, icon_path, callback)

    def register_parser(self, name, parser_func):
        """
        注册自定义文本解析器
        parser_func: 函数，接受 (text) 参数，返回角色对象或 None
        """
        if not self.app:
            return
        self.app.register_plugin_parser(name, parser_func)

    def register_game_mode(self, mode_id, name, character_class, field_patterns):
        """
        注册新的游戏模式（插件扩展新TRPG系统）
        mode_id: 模式标识符（如 "shadowrun"）
        name: 显示名称（如 "暗影狂奔"）
        character_class: 角色模型类
        field_patterns: 字段匹配模式字典
        """
        if not self.app:
            return
        self.app.register_plugin_mode(mode_id, name, character_class, field_patterns)

    def add_tab(self, tab_id, title, widget):
        """
        向主窗口添加一个新标签页
        tab_id: 标签页标识
        title: 标签页标题
        widget: QWidget 实例
        """
        if not self.main_window:
            return
        self.main_window.add_plugin_tab(tab_id, title, widget)
