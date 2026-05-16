"""
路径管理 — 解决 PyInstaller 打包后文件和目录的定位问题
确保 .exe 运行时在它旁边自动创建 data/、plugins/ 等目录
"""
import sys
import os
from pathlib import Path


def get_app_base():
    """
    获取应用程序基础目录

    - 打包为 .exe 后 → .exe 所在的目录
    - 源码运行时 → 项目根目录（COC-DND-Manager/）
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包模式：.exe 所在位置
        return Path(sys.executable).parent
    else:
        # 源码模式：本项目根目录
        return Path(__file__).parent.parent


def get_data_dir():
    """获取数据目录（存放 SQLite 数据库文件），不存在则自动创建"""
    data_dir = get_app_base() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir)


def get_db_path():
    """获取数据库完整路径"""
    return str(Path(get_data_dir()) / "characters.db")


def get_plugins_dir():
    """获取插件目录，不存在则自动创建"""
    plugins_dir = get_app_base() / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    return str(plugins_dir)


def get_settings_path():
    """获取设置 JSON 文件路径"""
    return str(Path(get_data_dir()) / "settings.json")


def load_settings_json():
    """直接加载设置（无缓存的简单读取）"""
    import json
    p = get_settings_path()
    if Path(p).exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings_json(data):
    """直接保存设置"""
    import json
    p = get_settings_path()
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ensure_dirs():
    """确保所有必要的目录都存在（启动时调用一次）"""
    get_data_dir()       # data/
    get_plugins_dir()    # plugins/
    # 如果还有需要自动创建的目录，在这里添加
