"""
Modern Dark Theme Qt Stylesheet for Desktop Utility UI.
Features clean typography, sleek dark palette, subtle borders, and smooth hover effects.
"""

DARK_STYLESHEET = """
/* Global Window and Base Widget Styling */
QMainWindow, QDialog {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #f8fafc;
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

/* Card Panels */
QFrame#CardPanel {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

/* Tabs Styling */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #0f172a;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
    padding: 9px 20px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: #0f172a;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background: #334155;
    color: #e2e8f0;
}

/* Push Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #475569;
    border-radius: 5px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #64748b;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton#PrimaryButton {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #38bdf8;
    font-weight: 600;
}

QPushButton#PrimaryButton:hover {
    background-color: #0369a1;
}

QPushButton#PrimaryButton:pressed {
    background-color: #075985;
}

QPushButton#FavoriteButton {
    background-color: #b45309;
    color: #ffffff;
    border: 1px solid #f59e0b;
    font-weight: 600;
}

QPushButton#FavoriteButton:hover {
    background-color: #d97706;
}

QPushButton#DangerButton {
    background-color: #b91c1c;
    color: #ffffff;
    border: 1px solid #ef4444;
}

QPushButton#DangerButton:hover {
    background-color: #991b1b;
}

/* Input Fields and Dropdowns */
QLineEdit, QComboBox, QSpinBox {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 5px;
    padding: 6px 10px;
    selection-background-color: #0284c7;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #38bdf8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left-width: 0px;
}

/* Group Boxes */
QGroupBox {
    border: 1px solid #334155;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 14px;
    font-weight: 600;
    color: #38bdf8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
}

/* List and Grid Views */
QListWidget {
    background-color: #020617;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #1e293b;
    background-color: #0f172a;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #0369a1;
    border-color: #38bdf8;
    color: #ffffff;
}

QListWidget::item:hover:!selected {
    background-color: #1e293b;
    border-color: #475569;
}

/* Scroll Bars */
QScrollBar:vertical {
    border: none;
    background: #0f172a;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #020617;
    color: #94a3b8;
    border-top: 1px solid #1e293b;
    padding: 4px;
}

/* Context Menus */
QMenu {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px 0px;
}

QMenu::item {
    padding: 8px 24px;
}

QMenu::item:selected {
    background-color: #0284c7;
    color: #ffffff;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background: #1e293b;
}

QCheckBox::indicator:checked {
    background: #0284c7;
    border-color: #38bdf8;
}
"""
