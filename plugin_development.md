# 🔌 插件开发手册 Plugin Development Guide

本手册介绍如何为「COC & DND 角色卡管理器」开发插件。
适用于有一定 Python 基础的开发者。

---

## 📋 目录

1. [插件系统概述](#1-插件系统概述)
2. [快速开始：你的第一个插件](#2-快速开始你的第一个插件)
3. [插件基类 API 参考](#3-插件基类-api-参考)
4. [生命周期钩子详解](#4-生命周期钩子详解)
5. [实战示例](#5-实战示例)
6. [调试与发布](#6-调试与发布)

---

## 1. 插件系统概述

### 插件可以做什么？

| 能力 | 说明 | 难度 |
|------|------|------|
| ✅ 添加菜单项 | 在顶部栏添加自定义按钮 | ⭐ |
| ✅ 监听角色事件 | 角色创建/修改/删除时自动处理 | ⭐ |
| ✅ 自定义解析器 | 支持新的文本格式导入 | ⭐⭐ |
| ✅ 添加游戏模式 | 注册全新的TRPG系统（如暗影狂奔） | ⭐⭐⭐ |
| ✅ 修改搜索 | 自定义搜索逻辑或结果排序 | ⭐⭐ |
| ✅ 云同步 | 将角色数据同步到云端 | ⭐⭐⭐ |
| ✅ 注入 UI | 添加新的标签页、面板 | ⭐⭐⭐⭐ |

### 插件工作原理

```
plugins/my_plugin/
├── __init__.py      # 插件主文件（必须）
├── requirements.txt # 额外依赖（可选）
└── ...              # 其他模块（可选）
```

插件本质上是一个 Python 包，放在 `plugins/` 目录下，程序启动时自动扫描加载。

---

## 2. 快速开始：你的第一个插件

### 步骤 1：创建插件目录

```
plugins/
└── hello_world/
    └── __init__.py
```

### 步骤 2：编写插件代码

```python
# plugins/hello_world/__init__.py
from character_manager.plugin.plugin_base import PluginBase


class HelloWorldPlugin(PluginBase):
    """一个简单的示例插件"""

    PLUGIN_NAME = "Hello World"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "我的第一个插件！在创建角色时弹窗问候"

    def on_character_created(self, character):
        """每次创建新角色时弹窗"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "👋 Hello World 插件",
            f"欢迎新角色「{character.name}」加入冒险！"
        )
```

### 步骤 3：运行测试

```bash
python main.py
```

程序启动后会自动加载 `hello_world` 插件。每次创建新角色时，你会看到一个欢迎弹窗。

---

## 3. 插件基类 API 参考

所有插件必须继承 `PluginBase`，下面是可以覆写的方法：

### 必须定义的属性

```python
PLUGIN_NAME = "插件名称"          # 显示用
PLUGIN_VERSION = "1.0.0"         # 版本号
PLUGIN_DESCRIPTION = "插件描述"   # 说明文字
```

### 生命周期钩子

| 方法 | 调用时机 | 说明 |
|------|---------|------|
| `on_load(app)` | 插件被加载时 | app 是应用实例，可访问数据库 |
| `on_ui_ready(window)` | 主窗口就绪 | window 是主窗口，可注入 UI |
| `on_enable()` | 插件启用时 | 进行初始化 |
| `on_disable()` | 插件禁用时 | 清理资源 |
| `on_unload()` | 插件卸载时 | 最终清理 |

### 业务钩子（按调用顺序）

| 方法 | 参数 | 说明 |
|------|------|------|
| `on_mode_switch(mode)` | `"coc"` 或 `"dnd"` | 用户切换模式时 |
| `on_character_created(character)` | 角色对象 | 新角色保存后 |
| `on_character_updated(character)` | 角色对象 | 角色更新后 |
| `on_character_deleted(character)` | 角色对象 | 角色删除前 |
| `on_search(query, filters, results)` | 查询+结果 | 可修改搜索结果并返回 |

### UI 注入方法（在 on_ui_ready 中使用）

| 方法 | 参数 | 说明 |
|------|------|------|
| `add_menu_item(menu, text, callback)` | 菜单名、文字、回调 | 添加菜单按钮 |
| `add_toolbar_button(text, icon_path, callback)` | 文字、图标、回调 | 添加工具栏按钮 |
| `register_parser(name, func)` | 名称、解析函数 | 注册自定义文本解析器 |
| `register_game_mode(id, name, cls, patterns)` | 标识、名称、模型、字段模式 | 注册新游戏模式 |
| `add_tab(id, title, widget)` | 标识、标题、QWidget | 添加新标签页 |

---

## 4. 生命周期钩子详解

### 4.1 `on_load(app)` — 插件加载

在此阶段可以访问数据库，但 UI 尚未就绪。

```python
def on_load(self, app):
    """app 包含核心服务"""
    # 访问数据库仓库
    self.repo = app.repository
    
    # 或者获取插件管理器（不太常见）
    self.plugin_manager = app.plugin_manager
```

> **注意**: `app` 参数就是 `MainWindow` 实例本身。在 `main_window.py` 中，`MainWindow.__init__` 保存了 `self.app = app`，并通过 `self.repository` 和 `self.plugin_manager` 暴露核心服务。

### 4.2 `on_ui_ready(window)` — UI 就绪

此时主窗口已经完全构建，可以注入 UI 元素。

```python
def on_ui_ready(self, main_window):
    # 保存主窗口引用（基类已自动保存到 self.main_window）
    # 添加工具栏按钮
    self.add_toolbar_button(
        text="🗃️ 导出",
        callback=self.export_characters
    )
    
    # 添加菜单项
    self.add_menu_item(
        menu_name="插件",
        item_text="导出全部角色",
        callback=self.export_characters
    )

def export_characters(self):
    """导出全部角色为 JSON"""
    import json
    from PySide6.QtWidgets import QFileDialog, QMessageBox
    
    chars = self.main_window.repository.get_all(self.main_window.current_mode)
    data = [c.to_dict() for c in chars]
    
    path, _ = QFileDialog.getSaveFileName(
        self.main_window, "保存导出", "characters.json",
        "JSON Files (*.json)"
    )
    if path:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(None, "导出成功", f"已导出 {len(data)} 个角色到\n{path}")
```

### 4.3 `on_character_created(character)` — 角色创建

```python
def on_character_created(self, character):
    """自动给新角色添加默认装备"""
    if self.main_window.current_mode == "dnd":
        # 自动添加新手装备
        import json
        equipment = json.loads(character.equipment) if isinstance(character.equipment, str) else character.equipment
        equipment.append("新手背包")
        equipment.append("10gp")
        character.equipment = json.dumps(equipment, ensure_ascii=False)
```

### 4.4 `on_mode_switch(mode)` — 模式切换

```python
def on_mode_switch(self, mode):
    """切换模式时更新插件的状态"""
    print(f"切换到 {'COC' if mode == 'coc' else 'DND'} 模式")
```

### 4.5 `on_search(query, filters, results)` — 修改搜索结果

```python
def on_search(self, query, filters, results):
    """
    在搜索结果中优先显示等级高的角色
    返回修改后的结果列表
    """
    if self.main_window.current_mode == "dnd":
        results.sort(key=lambda c: getattr(c, 'level', 1), reverse=True)
    return results
```

---

## 5. 实战示例

### 示例 1：云同步插件

```python
# plugins/cloud_sync/__init__.py
"""
云同步插件 — 将角色数据同步到自定义服务器
"""
import json
import urllib.request
from character_manager.plugin.plugin_base import PluginBase


class CloudSyncPlugin(PluginBase):
    PLUGIN_NAME = "云同步"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "将角色数据自动同步到云端服务器"

    SYNC_URL = "https://your-server.com/api/sync"

    def on_ui_ready(self, window):
        self.add_menu_item("插件", "☁️ 立即同步", self.sync_now)
        self.add_menu_item("插件", "⚙️ 云同步设置", self.show_settings)

    def on_character_created(self, character):
        self._upload_character(character)

    def on_character_updated(self, character):
        self._upload_character(character)

    def _upload_character(self, character):
        """上传角色到云端"""
        try:
            data = json.dumps(character.to_dict(), ensure_ascii=False).encode()
            req = urllib.request.Request(
                self.SYNC_URL,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print(f"同步失败: {e}")

    def sync_now(self):
        """立即同步所有角色"""
        from PySide6.QtWidgets import QMessageBox
        chars = self.main_window.repository.get_all(self.main_window.current_mode)
        for c in chars:
            self._upload_character(c)
        QMessageBox.information(None, "同步完成", f"已同步 {len(chars)} 个角色")

    def show_settings(self):
        """显示设置对话框"""
        from PySide6.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(
            None, "云同步设置", "服务器地址:",
            text=self.SYNC_URL
        )
        if ok and url:
            self.SYNC_URL = url
```

### 示例 2：添加新的游戏模式

```python
# plugins/custom_system/__init__.py
"""
自定义游戏模式插件示例
演示如何添加一个全新的TRPG系统模式
"""


class CustomCharacter:
    """自定义游戏的角色模型（简化版）"""

    def __init__(self):
        self.id = None
        self.name = "未命名"
        self.system = "custom"
        self.stats = {"力量": 10, "敏捷": 10, "意志": 10}
        self.skills = {}
        self.created_at = None
        self.updated_at = None

    def to_dict(self):
        import json
        from datetime import datetime
        return {
            "id": self.id, "name": self.name, "system": self.system,
            "stats": json.dumps(self.stats),
            "skills": json.dumps(self.skills),
        }

    @classmethod
    def from_dict(cls, data):
        import json
        c = cls()
        c.id = data.get("id")
        c.name = data.get("name", "未命名")
        c.stats = json.loads(data.get("stats", "{}"))
        c.skills = json.loads(data.get("skills", "{}"))
        return c

    def get_card_summary(self):
        return {
            "name": self.name,
            "subtitle": "自定义模式",
            "mode": "CUSTOM",
            "lines": [f"{k}: {v}" for k, v in self.stats.items()],
        }


def custom_parser(text):
    """自定义文本解析函数"""
    import re
    c = CustomCharacter()
    m = re.search(r"姓名\s*[:：]\s*(.+)", text)
    if m:
        c.name = m.group(1).strip()
    return c


class CustomModePlugin(PluginBase):
    PLUGIN_NAME = "自定义模式"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "添加一个自定义TRPG游戏模式"

    def on_load(self, app):
        # 注册自定义文本解析器
        self.register_parser("custom", custom_parser)
        
        # 注册新游戏模式 — 这会告诉系统"我新增了一个模式叫 custom"
        # 注意：当前版本需要在 UI 中手动添加模式按钮
        # app.register_plugin_mode("custom", "自定义模式", CustomCharacter, {})

    def on_ui_ready(self, window):
        self.add_menu_item("插件", "📝 新建自定义角色", self.create_custom)

    def create_custom(self):
        """创建一个自定义模式角色"""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(None, "新建角色", "角色名:")
        if ok and name:
            char = CustomCharacter()
            char.name = name
            # 保存到数据库（使用 COC 表作为通用存储，或自行建表）
            from character_manager.database.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO coc_characters (name) VALUES (?)",
                (name,)
            )
            conn.commit()
            char.id = cursor.lastrowid
            conn.close()
```

### 示例 3：数据导出插件

```python
# plugins/data_export/__init__.py
"""
数据导出插件 — 导出角色卡为各种格式
"""
import json
import csv
import io
from character_manager.plugin.plugin_base import PluginBase


class DataExportPlugin(PluginBase):
    PLUGIN_NAME = "数据导出"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "将角色卡导出为 JSON / CSV / 纯文本格式"

    def on_ui_ready(self, window):
        self.add_menu_item("插件", "📤 导出为 JSON", lambda: self.export("json"))
        self.add_menu_item("插件", "📤 导出为 CSV", lambda: self.export("csv"))
        self.add_menu_item("插件", "📤 导出为 文本", lambda: self.export("txt"))

    def export(self, fmt):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        chars = self.main_window.repository.get_all(self.main_window.current_mode)
        data = [c.to_dict() for c in chars]
        
        path, _ = QFileDialog.getSaveFileName(
            None, "导出",
            f"characters.{fmt}",
            f"*.{fmt.upper()} Files (*.{fmt})"
        )
        if not path:
            return

        text = ""
        if fmt == "json":
            text = json.dumps(data, ensure_ascii=False, indent=2)
        elif fmt == "csv":
            if data:
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                text = output.getvalue()
        elif fmt == "txt":
            lines = []
            for c in chars:
                summary = c.get_card_summary()
                lines.append(f"【{summary['name']}】{summary['subtitle']}")
                lines.extend(summary['lines'])
                lines.append("---")
            text = "\n".join(lines)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        QMessageBox.information(None, "导出成功",
            f"已导出 {len(chars)} 个角色到\n{path}")
```

---

## 6. 调试与发布

### 调试建议

1. **插件加载失败怎么办？**
   ```
   # 查看控制台输出了解错误详情
   程序启动时会在终端打印插件加载错误信息
   ```

2. **使用 print 调试**
   ```python
   def on_load(self, app):
       print(f"🔄 插件 {self.PLUGIN_NAME} 正在加载...")
       # 你的代码
       print(f"✅ 插件 {self.PLUGIN_NAME} 加载成功")
   ```

3. **捕获异常避免插件崩溃影响主程序**
   ```python
   def on_character_created(self, character):
       try:
           # 你的逻辑
           pass
       except Exception as e:
           print(f"插件错误: {e}")
   ```

### 发布清单

发布插件前请检查：

- [ ] `PLUGIN_NAME`, `PLUGIN_VERSION`, `PLUGIN_DESCRIPTION` 已正确填写
- [ ] `__init__.py` 中包含了插件类
- [ ] 插件类继承了 `PluginBase`
- [ ] 所有异常已被妥善捕获
- [ ] 已将插件文件夹放入 `plugins/` 目录测试通过

### 插件分发方式

1. 直接将插件文件夹发给用户
2. 用户放入应用的 `plugins/` 目录
3. 重启应用即可加载

---

## 💡 贴士与最佳实践

1. **保持轻量** — 插件应尽量轻量，避免阻塞主线程
2. **异常安全** — 所有钩子函数都应该 try/except，避免一个插件崩溃影响整个应用
3. **善用 JSON** — 技能、装备等复杂字段使用 JSON 格式存储
4. **监听而非接管** — 尽量用钩子监听事件，而不是直接修改核心代码
5. **善用日志** — 使用 `print()` 输出调试信息到控制台

---

## ❓ 常见问题

**Q: 插件如何更新？**
A: 替换 `plugins/` 下的对应文件夹即可，重启应用生效。

**Q: 一个插件可以是多个文件吗？**
A: 可以。`__init__.py` 是入口，可以在同目录下创建多个 .py 文件，用 `from .other_module import ...` 导入。

**Q: 可以同时加载多个插件吗？**
A: 可以。`plugins/` 下的所有合法插件都会自动加载，互不干扰。

**Q: 插件可以有自己的依赖吗？**
A: 可以，在插件目录下放一个 `requirements.txt`，用户需要手动安装这些依赖。

**Q: 如何禁用某个插件？**
A: 暂时移除该插件文件夹（移到 plugins 外），或重命名文件夹使其不以合法 Python 包格式存在。

---

## 7. 可用服务：网络桥接插件

`network_bridge` 插件不仅提供联机功能，还开放了 **WebAccess** 互联网接入服务。  
其他插件可以直接调用它来**联网搜索、获取网页内容**，无需自己处理网络请求。

### 7.1 获取 WebAccess 实例

```python
def on_ui_ready(self, main_window):
    # 获取 network_bridge 插件
    bridge = main_window.plugin_manager.get_plugin("network_bridge")
    if bridge:
        web = bridge.get_web_access()
        self.web = web
```

### 7.2 联网搜索

```python
results = self.web.search("COC 暗影之屋 攻略")
# 返回: [{title, url, snippet}, ...]
```

### 7.3 获取网页内容

```python
html = self.web.fetch_text("https://example.com/scenario")
json_data = self.web.fetch_json("https://api.example.com/data")
```

### 7.4 搜索 TRPG 剧本

```python
scenarios = self.web.search_scenario("1920年代 神秘谋杀")
```

### 7.5 监听联机事件

联机插件也提供了事件系统，其他插件可以监听房间内的事件：

```python
def on_ui_ready(self, main_window):
    bridge = main_window.plugin_manager.get_plugin("network_bridge")
    if bridge and hasattr(bridge, 'network_ui'):
        panel = bridge.network_ui
        # 当有玩家发言时处理
        # 联机面板将聊天气泡渲染在界面上
```

### 7.6 联机消息格式

所有网络消息使用 JSON 格式，类型定义在 `plugins/network_bridge/protocol.py`：

```python
MSG_CHAT = "chat"         # 玩家聊天
MSG_ROLL = "roll"         # 掷骰结果
MSG_AI_REPLY = "ai_reply" # AI 回复广播
MSG_STATUS = "status"     # 角色状态更新
```

---

> 如果还有问题，或者想开发特定功能的插件但不知如何下手，随时通过 Reasonix Code 问我！😊
