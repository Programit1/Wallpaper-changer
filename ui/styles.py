"""
Pinterest-Inspired Restrained Dark Palette Qt Stylesheet.
Features dark matte backgrounds, subtle card overlays, minimal borders, and clean typography.
"""

DARK_STYLESHEET = """
/* Base Window and Dialog Styling */
QMainWindow, QDialog {
    background-color: #090d16;
    color: #f8fafc;
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #f8fafc;
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

/* Header & Top Bar */
QLineEdit#SearchBar {
    background-color: #111827;
    color: #f8fafc;
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 8px 18px;
    font-size: 14px;
    selection-background-color: #0284c7;
}

QLineEdit#SearchBar:focus {
    border: 1px solid #38bdf8;
    background-color: #1f2937;
}

/* Sidebar Styling */
QFrame#SidebarFrame {
    background-color: #0d1322;
    border-right: 1px solid #1e293b;
}

QLabel#SidebarHeader {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #38bdf8;
    padding: 10px 12px 4px 12px;
}

QLabel#SidebarSection {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    padding: 12px 12px 4px 12px;
    letter-spacing: 0.5px;
}

QListWidget#SidebarList {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#SidebarList::item {
    padding: 8px 12px;
    border-radius: 6px;
    color: #cbd5e1;
    font-weight: 500;
    margin-bottom: 2px;
}

QListWidget#SidebarList::item:selected {
    background-color: #1e293b;
    color: #38bdf8;
    font-weight: 600;
}

QListWidget#SidebarList::item:hover:!selected {
    background-color: #172033;
    color: #f8fafc;
}

/* Push Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton#PrimaryButton {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #38bdf8;
    font-weight: 600;
    border-radius: 6px;
}

QPushButton#PrimaryButton:hover {
    background-color: #0369a1;
}

QPushButton#FavoriteButton {
    background-color: #b45309;
    color: #ffffff;
    border: 1px solid #f59e0b;
    font-weight: 600;
    border-radius: 6px;
}

QPushButton#FavoriteButton:hover {
    background-color: #d97706;
}

QPushButton#DangerButton {
    background-color: #b91c1c;
    color: #ffffff;
    border: 1px solid #ef4444;
    border-radius: 6px;
}

QPushButton#DangerButton:hover {
    background-color: #991b1b;
}

/* Overlay Quick Action Buttons */
QPushButton#OverlayBtn {
    background-color: rgba(15, 23, 42, 0.85);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 12px;
}

QPushButton#OverlayBtn:hover {
    background-color: rgba(2, 132, 199, 0.95);
    border-color: #38bdf8;
}

/* Masonry Scroll Area */
QScrollArea#MasonryScroll {
    background-color: #090d16;
    border: none;
}

QWidget#MasonryContainer {
    background-color: #090d16;
}

/* Tabs Styling */
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #090d16;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background: #111827;
    color: #94a3b8;
    border: 1px solid #1e293b;
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: #090d16;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
    font-weight: 600;
}

/* Scroll Bars */
QScrollBar:vertical {
    border: none;
    background: #090d16;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #1e293b;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #334155;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #070a12;
    color: #64748b;
    border-top: 1px solid #1e293b;
    padding: 4px;
}
"""
