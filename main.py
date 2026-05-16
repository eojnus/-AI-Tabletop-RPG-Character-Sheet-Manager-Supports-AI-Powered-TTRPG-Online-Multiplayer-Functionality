#!/usr/bin/env python3
"""
COC & DND 角色卡管理器 — 启动入口

一个 Windows 桌面应用，用于管理 COC 7th 和 DND 5e 跑团角色卡。
支持卡片式展示、智能文本导入、多维搜索排序、插件扩展。

使用方式:
    pip install PySide6
    python main.py

打包为 .exe:
    pip install pyinstaller
    pyinstaller --windowed --onefile --name "角色卡管理器" --icon resources/icon.ico main.py
"""
import sys
import os

# 确保项目根目录在 Python 路径中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from character_manager.paths import ensure_dirs
from character_manager.database.database import init_database
from character_manager.ui.main_window import MainWindow


def setup_high_dpi():
    """配置高 DPI 支持"""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )


def main():
    # 确保必要目录存在（.exe 旁边创建 data/、plugins/）
    ensure_dirs()

    # 初始化数据库（创建表）
    init_database()

    # 创建应用
    setup_high_dpi()
    app = QApplication(sys.argv)
    app.setApplicationName("COC & DND 角色卡管理器")
    app.setOrganizationName("CharacterManager")

    # 启用磨砂玻璃效果（Windows 11 模糊效果）
    try:
        from PySide6.QtCore import QLibraryInfo
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    except Exception:
        pass

    # 创建并显示主窗口
    window = MainWindow(app=app)
    window.show()

    # 运行事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
