"""
主题管理器 — 定义多套配色方案，支持动态切换
"""
import json
import os
from pathlib import Path

# ==================== 主题定义 ====================

THEMES = {
    "深空暗黑": {
        "type": "dark",
        "colors": {
            "bg_start": "#0d0d1a",
            "bg_end": "#1a1a2e",
            "surface": "rgba(255,255,255,0.06)",
            "surface_hover": "rgba(255,255,255,0.10)",
            "surface_card": "rgba(255,255,255,0.06)",
            "text_primary": "#ffffff",
            "text_secondary": "rgba(255,255,255,0.5)",
            "text_body": "rgba(255,255,255,0.85)",
            "accent": "#6c63ff",
            "accent_bg": "rgba(108,99,255,0.18)",
            "accent_hover": "rgba(108,99,255,0.35)",
            "border": "rgba(255,255,255,0.08)",
            "border_focus": "rgba(108,99,255,0.4)",
            "input_bg": "rgba(0,0,0,0.2)",
            "danger": "#ff4444",
            "danger_bg": "rgba(255,60,60,0.12)",
        }
    },
    "素白明亮": {
        "type": "light",
        "colors": {
            "bg_start": "#f0f0f5",
            "bg_end": "#e4e4ec",
            "surface": "rgba(255,255,255,0.7)",
            "surface_hover": "rgba(255,255,255,0.85)",
            "surface_card": "rgba(255,255,255,0.8)",
            "text_primary": "#1a1a2e",
            "text_secondary": "rgba(0,0,0,0.4)",
            "text_body": "rgba(0,0,0,0.8)",
            "accent": "#6c63ff",
            "accent_bg": "rgba(108,99,255,0.15)",
            "accent_hover": "rgba(108,99,255,0.25)",
            "border": "rgba(0,0,0,0.1)",
            "border_focus": "rgba(108,99,255,0.4)",
            "input_bg": "rgba(255,255,255,0.6)",
            "danger": "#d32f2f",
            "danger_bg": "rgba(211,47,47,0.1)",
        }
    },
    "暗夜紫": {
        "type": "dark",
        "colors": {
            "bg_start": "#0d0a1a",
            "bg_end": "#1a1030",
            "surface": "rgba(120,80,200,0.08)",
            "surface_hover": "rgba(120,80,200,0.15)",
            "surface_card": "rgba(120,80,200,0.06)",
            "text_primary": "#ffffff",
            "text_secondary": "rgba(200,180,255,0.5)",
            "text_body": "rgba(200,180,255,0.85)",
            "accent": "#9c6eff",
            "accent_bg": "rgba(156,110,255,0.18)",
            "accent_hover": "rgba(156,110,255,0.35)",
            "border": "rgba(156,110,255,0.12)",
            "border_focus": "rgba(156,110,255,0.4)",
            "input_bg": "rgba(0,0,0,0.3)",
            "danger": "#ff6b6b",
            "danger_bg": "rgba(255,60,60,0.12)",
        }
    },
    "森林绿": {
        "type": "dark",
        "colors": {
            "bg_start": "#0a1a0d",
            "bg_end": "#0f2614",
            "surface": "rgba(60,180,100,0.06)",
            "surface_hover": "rgba(60,180,100,0.12)",
            "surface_card": "rgba(60,180,100,0.05)",
            "text_primary": "#ffffff",
            "text_secondary": "rgba(160,220,180,0.5)",
            "text_body": "rgba(180,230,200,0.85)",
            "accent": "#3dd68c",
            "accent_bg": "rgba(61,214,140,0.18)",
            "accent_hover": "rgba(61,214,140,0.35)",
            "border": "rgba(61,214,140,0.12)",
            "border_focus": "rgba(61,214,140,0.4)",
            "input_bg": "rgba(0,0,0,0.3)",
            "danger": "#ff6b6b",
            "danger_bg": "rgba(255,60,60,0.12)",
        }
    },
}

DEFAULT_THEME = "深空暗黑"
DEFAULT_FONT_FAMILY = "Microsoft YaHei"
DEFAULT_FONT_SIZE = 13

# ==================== 设置管理器 ====================

from ..paths import get_settings_path

SETTINGS_PATH = get_settings_path()


def _settings_path():
    """返回 Path 对象"""
    from pathlib import Path
    return Path(SETTINGS_PATH)


def load_settings():
    """加载用户设置"""
    p = _settings_path()
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings):
    """保存用户设置"""
    p = _settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_setting(key, default=None):
    """获取单项设置"""
    return load_settings().get(key, default)


def apply_theme(window, theme_name=None):
    """应用主题到窗口"""
    from .theme_manager import THEMES, get_setting
    if theme_name is None:
        theme_name = get_setting("theme", DEFAULT_THEME)
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    colors = theme["colors"]

    font_family = get_setting("font_family", DEFAULT_FONT_FAMILY)
    font_size = get_setting("font_size", DEFAULT_FONT_SIZE)

    # 生成 QSS 样式表
    qss = _generate_qss(colors, font_family, font_size)
    window.setStyleSheet(qss)

    # 保存主题到设置
    settings = load_settings()
    settings["theme"] = theme_name
    save_settings(settings)


def _generate_qss(colors, font_family, font_size):
    """根据主题颜色生成 QSS 样式表"""
    c = colors
    return f"""
    QMainWindow {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 {c["bg_start"]}, stop:1 {c["bg_end"]});
    }}
    QWidget {{
        color: {c["text_body"]};
        font-family: "{font_family}";
        font-size: {font_size}px;
    }}
    #navPanel {{
        background: {c["surface"]};
        border-right: 1px solid {c["border"]};
        min-width: 140px;
        max-width: 180px;
    }}
    #navTitle {{
        color: {c["text_secondary"]};
        font-size: {max(10, font_size-2)}px;
        font-weight: bold;
        padding: 16px 12px 8px 12px;
    }}
    QPushButton#navButton {{
        background: transparent;
        color: {c["text_secondary"]};
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-size: {font_size}px;
        margin: 2px 8px;
    }}
    QPushButton#navButton:hover {{
        background: {c["accent_bg"]};
        color: {c["text_primary"]};
    }}
    QPushButton#navButton:checked {{
        background: {c["accent_bg"]};
        color: {c["text_primary"]};
        border-left: 3px solid {c["accent"]};
    }}
    #searchBar {{
        background: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 20px;
        padding: 8px 16px;
        color: {c["text_primary"]};
        font-size: {font_size}px;
        min-height: 20px;
    }}
    #searchBar:focus {{
        border: 1px solid {c["border_focus"]};
        background: {c["surface_hover"]};
    }}
    QComboBox {{
        background: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        padding: 6px 12px;
        color: {c["text_body"]};
        font-size: {max(12, font_size-1)}px;
        min-width: 70px;
    }}
    QComboBox:hover {{
        border: 1px solid {c["accent"]};
    }}
    QComboBox QAbstractItemView {{
        background: {c["bg_end"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        selection-background-color: {c["accent_bg"]};
        color: {c["text_body"]};
        padding: 4px;
    }}
    #cardWidget {{
        background: {c["surface_card"]};
        border: 1px solid {c["border"]};
        border-radius: 16px;
        padding: 16px;
        min-width: 200px;
        max-width: 240px;
        min-height: 180px;
    }}
    #cardWidget:hover {{
        background: {c["surface_hover"]};
        border: 1px solid {c["accent"]};
    }}
    #modeIndicator {{
        font-size: 10px;
        font-weight: bold;
        color: {c["accent"]};
        background: {c["accent_bg"]};
        border-radius: 4px;
        padding: 2px 8px;
    }}
    #titleLabel {{
        font-size: {font_size+8}px;
        font-weight: bold;
        color: {c["text_primary"]};
    }}
    #subtitleLabel {{
        font-size: {font_size+1}px;
        color: {c["text_secondary"]};
    }}
    #statLabel {{
        font-size: {max(11, font_size-2)}px;
        color: {c["text_secondary"]};
    }}
    QPushButton#actionButton {{
        background: {c["accent_bg"]};
        border: 1px solid {c["accent"]};
        border-radius: 10px;
        padding: 8px 18px;
        color: {c["text_primary"]};
        font-weight: 500;
        font-size: {font_size}px;
    }}
    QPushButton#actionButton:hover {{
        background: {c["accent_hover"]};
    }}
    QPushButton#dangerButton {{
        background: {c["danger_bg"]};
        border: 1px solid {c["danger"]};
        border-radius: 10px;
        padding: 8px 18px;
        color: {c["danger"]};
        font-weight: 500;
        font-size: {font_size}px;
    }}
    QPushButton#dangerButton:hover {{
        background: rgba(255,60,60,0.25);
    }}
    QPushButton#sortButton {{
        background: transparent;
        color: {c["text_secondary"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        padding: 4px 10px;
        font-size: {max(11, font_size-2)}px;
    }}
    QPushButton#sortButton:hover {{
        background: {c["surface_hover"]};
        color: {c["text_body"]};
    }}
    QPushButton#sortButton:checked {{
        background: {c["accent_bg"]};
        border: 1px solid {c["accent"]};
        color: {c["text_primary"]};
    }}
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background: {c["input_bg"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        padding: 10px 14px;
        color: {c["text_body"]};
        font-family: "{font_family}";
        font-size: {font_size}px;
        selection-background-color: {c["accent_bg"]};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {c["border_focus"]};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: {c["border"]};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c["text_secondary"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    QGroupBox {{
        background: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 12px;
        margin-top: 16px;
        padding: 16px 12px 12px 12px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 12px;
        color: {c["text_secondary"]};
        font-size: {max(11, font_size-2)}px;
    }}
    QTabWidget::pane {{
        background: {c["input_bg"]};
        border: none;
        border-radius: 8px;
        padding: 8px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {c["text_secondary"]};
        border: none;
        padding: 8px 20px;
        font-size: {font_size}px;
    }}
    QTabBar::tab:selected {{
        color: {c["text_primary"]};
        border-bottom: 2px solid {c["accent"]};
    }}
    QTabBar::tab:hover {{
        color: {c["text_body"]};
    }}
    QMessageBox {{
        background: {c["bg_end"]};
        border-radius: 12px;
    }}
    QMessageBox QLabel {{
        color: {c["text_primary"]};
    }}
    QMessageBox QPushButton {{
        background: {c["accent_bg"]};
        border: 1px solid {c["accent"]};
        border-radius: 8px;
        padding: 6px 20px;
        color: {c["text_primary"]};
        min-width: 60px;
    }}
    QMessageBox QPushButton:hover {{
        background: {c["accent_hover"]};
    }}
    #divider {{
        background: {c["border"]};
        max-height: 1px;
    }}
    QSpinBox {{
        background: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 6px;
        padding: 4px 8px;
        color: {c["text_body"]};
        font-size: {font_size}px;
    }}
    QSpinBox:focus {{
        border: 1px solid {c["border_focus"]};
    }}
    QDialog {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 {c["bg_start"]}, stop:1 {c["bg_end"]});
    }}
    QListWidget {{
        background: {c["input_bg"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        color: {c["text_body"]};
        font-size: {font_size}px;
    }}
    QListWidget::item {{
        padding: 8px 12px;
        border-radius: 6px;
    }}
    QListWidget::item:hover {{
        background: {c["surface_hover"]};
    }}
    QListWidget::item:selected {{
        background: {c["accent_bg"]};
        color: {c["text_primary"]};
    }}
    QSlider::groove:horizontal {{
        border: none;
        height: 4px;
        background: {c["border"]};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {c["accent"]};
        border: none;
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    QSlider::sub-page:horizontal {{
        background: {c["accent"]};
        border-radius: 2px;
    }}
    """
