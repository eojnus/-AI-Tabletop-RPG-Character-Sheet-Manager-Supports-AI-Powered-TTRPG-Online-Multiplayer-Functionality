"""
磨砂玻璃风格实现模块
提供深色磨砂玻璃主题的样式表和辅助函数
"""

# ==================== 全局 QSS 样式表 ====================

GLASS_STYLE_SHEET = """
/* ===== 全局设置 ===== */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0d0d1a, stop:1 #1a1a2e);
}

QWidget {
    color: rgba(255, 255, 255, 0.85);
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
}

/* ===== 导航栏 ===== */
#navPanel {
    background: rgba(255, 255, 255, 0.06);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
    min-width: 140px;
    max-width: 180px;
}

#navTitle {
    color: rgba(255, 255, 255, 0.5);
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 16px 12px 8px 12px;
    text-transform: uppercase;
}

/* ===== 导航按钮 ===== */
QPushButton#navButton {
    background: transparent;
    color: rgba(255, 255, 255, 0.6);
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    margin: 2px 8px;
}

QPushButton#navButton:hover {
    background: rgba(108, 99, 255, 0.15);
    color: rgba(255, 255, 255, 0.9);
}

QPushButton#navButton:checked {
    background: rgba(108, 99, 255, 0.25);
    color: #ffffff;
    border-left: 3px solid #6c63ff;
}

/* ===== 搜索栏 ===== */
#searchBar {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 8px 16px;
    color: white;
    font-size: 13px;
    min-height: 20px;
}

#searchBar:focus {
    border: 1px solid rgba(108, 99, 255, 0.5);
    background: rgba(255, 255, 255, 0.12);
}

/* ===== 下拉框/筛选框 ===== */
QComboBox {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 6px 12px;
    color: white;
    font-size: 12px;
    min-width: 80px;
}

QComboBox:hover {
    border: 1px solid rgba(108, 99, 255, 0.4);
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background: #1e1e35;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    selection-background-color: rgba(108, 99, 255, 0.3);
    color: white;
    padding: 4px;
    outline: none;
}

/* ===== 卡片容器 ===== */
#cardGridArea {
    background: transparent;
    border: none;
}

/* ===== 单张卡片 ===== */
#cardWidget {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px;
    min-width: 200px;
    max-width: 240px;
    min-height: 180px;
}

#cardWidget:hover {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(108, 99, 255, 0.3);
}

/* ===== 按钮 ===== */
QPushButton#actionButton {
    background: rgba(108, 99, 255, 0.2);
    border: 1px solid rgba(108, 99, 255, 0.3);
    border-radius: 10px;
    padding: 8px 18px;
    color: white;
    font-weight: 500;
    font-size: 13px;
}

QPushButton#actionButton:hover {
    background: rgba(108, 99, 255, 0.35);
    border: 1px solid rgba(108, 99, 255, 0.5);
}

QPushButton#actionButton:pressed {
    background: rgba(108, 99, 255, 0.5);
}

/* ===== 危险按钮（删除） ===== */
QPushButton#dangerButton {
    background: rgba(255, 60, 60, 0.15);
    border: 1px solid rgba(255, 60, 60, 0.25);
    border-radius: 10px;
    padding: 8px 18px;
    color: #ff6666;
    font-weight: 500;
    font-size: 13px;
}

QPushButton#dangerButton:hover {
    background: rgba(255, 60, 60, 0.3);
}

/* ===== 导入预览文本框 ===== */
QTextEdit, QPlainTextEdit {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 12px;
    color: rgba(255, 255, 255, 0.85);
    font-size: 13px;
    selection-background-color: rgba(108, 99, 255, 0.3);
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid rgba(108, 99, 255, 0.4);
}

/* ===== 标签 ===== */
QLabel {
    color: rgba(255, 255, 255, 0.8);
}

QLabel#titleLabel {
    font-size: 22px;
    font-weight: bold;
    color: white;
}

QLabel#subtitleLabel {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
}

QLabel#statLabel {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
}

QLabel#statValue {
    font-size: 16px;
    font-weight: bold;
    color: rgba(255, 255, 255, 0.9);
}

QLabel#modeIndicator {
    font-size: 10px;
    font-weight: bold;
    color: #6c63ff;
    background: rgba(108, 99, 255, 0.15);
    border-radius: 4px;
    padding: 2px 8px;
}

/* ===== 滚动条 ===== */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.25);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ===== 分割线 ===== */
QFrame#divider {
    background: rgba(255, 255, 255, 0.06);
    max-height: 1px;
}

/* ===== 分组框 ===== */
QGroupBox {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    margin-top: 16px;
    padding: 16px 12px 12px 12px;
    font-weight: 500;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: rgba(255, 255, 255, 0.6);
    font-size: 12px;
    font-weight: normal;
}

/* ===== 详情窗口 ===== */
#detailWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0d0d1a, stop:1 #1a1a2e);
    border-radius: 16px;
}

/* ===== 排序按钮组 ===== */
QPushButton#sortButton {
    background: transparent;
    color: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 11px;
}

QPushButton#sortButton:hover {
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.8);
}

QPushButton#sortButton:checked {
    background: rgba(108, 99, 255, 0.2);
    border: 1px solid rgba(108, 99, 255, 0.3);
    color: white;
}

/* ===== 消息弹窗 ===== */
QMessageBox {
    background: #1a1a2e;
    border-radius: 12px;
}

QMessageBox QLabel {
    color: white;
}

QMessageBox QPushButton {
    background: rgba(108, 99, 255, 0.2);
    border: 1px solid rgba(108, 99, 255, 0.3);
    border-radius: 8px;
    padding: 6px 20px;
    color: white;
    min-width: 60px;
}

QMessageBox QPushButton:hover {
    background: rgba(108, 99, 255, 0.35);
}
"""
