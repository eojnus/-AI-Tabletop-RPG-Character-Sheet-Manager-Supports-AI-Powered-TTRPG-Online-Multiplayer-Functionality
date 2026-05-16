"""
插件管理器 — 负责加载、卸载、启用、禁用插件
"""
import importlib
import inspect
import os
import sys
import traceback
from .plugin_base import PluginBase
from ..paths import get_plugins_dir


class PluginManager:
    """
    插件管理器
    - 扫描 plugins/ 目录加载插件
    - 管理插件的启用/禁用状态
    - 提供插件列表查询
    """

    def __init__(self, app):
        self.app = app
        self.plugins = {}          # name -> plugin_instance
        self.plugin_dirs = []      # 插件搜索路径
        self._plugin_actions = {}  # UI回调缓存
        self.load_errors = {}      # name -> error_msg 加载失败的记录

        # 默认插件目录（自动创建在 .exe 旁边）
        self.add_plugin_dir(get_plugins_dir())

    def add_plugin_dir(self, dir_path):
        """添加插件搜索目录"""
        if dir_path not in self.plugin_dirs:
            self.plugin_dirs.append(dir_path)
            if dir_path not in sys.path:
                sys.path.insert(0, dir_path)

    def discover_plugins(self):
        """
        扫描所有插件目录，发现可用的插件模块
        返回: [{name, path, loaded}]
        """
        discovered = []
        for dir_path in self.plugin_dirs:
            if not os.path.isdir(dir_path):
                continue
            for entry in os.listdir(dir_path):
                entry_path = os.path.join(dir_path, entry)
                # 每个子文件夹都是一个插件
                if os.path.isdir(entry_path):
                    init_file = os.path.join(entry_path, "__init__.py")
                    if os.path.isfile(init_file):
                        discovered.append({
                            "name": entry,
                            "path": entry_path,
                            "loaded": entry in self.plugins,
                        })
        return discovered

    def load_plugin(self, plugin_name):
        """
        加载指定插件
        返回: (success, message)
        """
        if plugin_name in self.plugins:
            return False, f"插件「{plugin_name}」已加载"

        try:
            # 尝试导入插件模块
            plugin_module = importlib.import_module(plugin_name)

            # 查找插件类（继承 PluginBase 的子类）
            plugin_class = None
            for name, obj in inspect.getmembers(plugin_module):
                if (inspect.isclass(obj) and
                        issubclass(obj, PluginBase) and
                        obj is not PluginBase):
                    plugin_class = obj
                    break

            if plugin_class is None:
                return False, f"插件「{plugin_name}」中未找到有效的插件类"

            # 实例化插件
            plugin_instance = plugin_class()
            plugin_instance.on_load(self.app)

            self.plugins[plugin_name] = plugin_instance
            return True, f"插件「{plugin_name} v{plugin_instance.PLUGIN_VERSION}」加载成功"

        except Exception as e:
            traceback.print_exc()
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.load_errors[plugin_name] = error_msg
            return False, f"加载插件「{plugin_name}」失败: {error_msg}"

    def load_all_plugins(self):
        """加载所有已发现的插件（跳过被禁用的）"""
        from ..paths import load_settings_json
        settings = load_settings_json()
        disabled = set(settings.get("disabled_plugins", []))

        discovered = self.discover_plugins()
        results = []
        for info in discovered:
            name = info["name"]
            if name in disabled:
                results.append({"name": name, "success": False, "message": "已禁用，跳过加载"})
                continue
            success, msg = self.load_plugin(name)
            results.append({"name": name, "success": success, "message": msg})
        return results

    def unload_plugin(self, plugin_name):
        """卸载指定插件"""
        if plugin_name not in self.plugins:
            return False, f"插件「{plugin_name}」未加载"

        plugin = self.plugins[plugin_name]
        try:
            plugin.on_disable()
            plugin.on_unload()
        except Exception as e:
            pass

        del self.plugins[plugin_name]
        return True, f"插件「{plugin_name}」已卸载"

    def enable_plugin(self, plugin_name):
        """启用插件"""
        if plugin_name not in self.plugins:
            return False, f"插件「{plugin_name}」未加载"
        plugin = self.plugins[plugin_name]
        plugin.enabled = True
        try:
            plugin.on_enable()
        except Exception as e:
            return False, f"启用插件失败: {str(e)}"
        return True, f"插件「{plugin_name}」已启用"

    def disable_plugin(self, plugin_name):
        """禁用插件"""
        if plugin_name not in self.plugins:
            return False, f"插件「{plugin_name}」未加载"
        plugin = self.plugins[plugin_name]
        plugin.enabled = False
        try:
            plugin.on_disable()
        except Exception as e:
            pass
        return True, f"插件「{plugin_name}」已禁用"

    def get_plugin(self, name):
        """获取插件实例"""
        return self.plugins.get(name)

    def get_all_plugins(self):
        """获取所有已加载的插件信息"""
        return [
            {
                "name": name,
                "instance": p,
                "enabled": p.enabled,
                "version": p.PLUGIN_VERSION,
                "description": p.PLUGIN_DESCRIPTION,
            }
            for name, p in self.plugins.items()
        ]

    def notify_ui_ready(self, main_window):
        """通知所有插件 UI 已就绪"""
        for name, plugin in self.plugins.items():
            try:
                plugin.app = self.app
                plugin.main_window = main_window
                plugin.on_ui_ready(main_window)
                if plugin.enabled:
                    plugin.on_enable()
            except Exception as e:
                print(f"插件「{name}」UI初始化失败: {e}")

    def notify_mode_switch(self, mode):
        """通知所有插件模式切换"""
        for name, plugin in self.plugins.items():
            if plugin.enabled:
                try:
                    plugin.on_mode_switch(mode)
                except Exception as e:
                    print(f"插件「{name}」模式切换处理失败: {e}")

    def notify_character_created(self, character):
        """通知所有插件角色创建"""
        for name, plugin in self.plugins.items():
            if plugin.enabled:
                try:
                    plugin.on_character_created(character)
                except Exception as e:
                    print(f"插件「{name}」创建通知失败: {e}")

    def notify_character_updated(self, character):
        """通知所有插件角色更新"""
        for name, plugin in self.plugins.items():
            if plugin.enabled:
                try:
                    plugin.on_character_updated(character)
                except Exception as e:
                    print(f"插件「{name}」更新通知失败: {e}")

    def notify_character_deleted(self, character):
        """通知所有插件角色删除"""
        for name, plugin in self.plugins.items():
            if plugin.enabled:
                try:
                    plugin.on_character_deleted(character)
                except Exception as e:
                    print(f"插件「{name}」删除通知失败: {e}")

    def notify_search(self, query, filters, results):
        """通知所有插件搜索事件，允许修改结果"""
        final_results = results
        for name, plugin in self.plugins.items():
            if plugin.enabled:
                try:
                    modified = plugin.on_search(query, filters, final_results)
                    if modified is not None:
                        final_results = modified
                except Exception as e:
                    print(f"插件「{name}」搜索处理失败: {e}")
        return final_results
