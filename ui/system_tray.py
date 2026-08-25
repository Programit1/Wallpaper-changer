"""
Windows System Tray Integration.
Provides context menu for quick controls (Next, Prev, Random, Settings, Exit).
"""

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QPolygon
from PyQt6.QtCore import QPoint


def create_tray_icon() -> QIcon:
    """Generates a clean programmatic tray icon pixmap if file icon isn't available."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(37, 99, 235))  # Accent blue
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 28, 28, 6, 6)

    painter.setBrush(QColor(255, 255, 255))
    painter.drawEllipse(7, 7, 6, 6)
    points = [
        (6, 24), (12, 14), (18, 24),
        (15, 24), (20, 17), (26, 24)
    ]
    poly = QPolygon([QPoint(x, y) for x, y in points])
    painter.drawPolygon(poly)
    painter.end()
    return QIcon(pixmap)


class SystemTrayIcon(QObject):
    """System Tray controller."""
    open_main_requested = pyqtSignal()
    open_library_requested = pyqtSignal()
    open_settings_requested = pyqtSignal()
    exit_requested = pyqtSignal()

    def __init__(self, wallpaper_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.tray_icon = QSystemTrayIcon(parent)
        self.tray_icon.setIcon(create_tray_icon())
        self.tray_icon.setToolTip("Wallhaven Wallpaper Changer")

        self.menu = QMenu()
        self._build_menu()

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

        self.wm.wallpaper_changed.connect(self.update_wallpaper_title)

    def _build_menu(self):
        self.menu.clear()

        # Current Wallpaper Info Header
        self.title_action = self.menu.addAction("Current: Loading...")
        self.title_action.setEnabled(False)

        self.menu.addSeparator()

        # Quick Actions
        self.action_next = self.menu.addAction("Next Wallpaper")
        self.action_next.triggered.connect(self.wm.fetch_next_in_history)

        self.action_prev = self.menu.addAction("Previous Wallpaper")
        self.action_prev.triggered.connect(self.wm.fetch_previous_wallpaper)

        self.action_random = self.menu.addAction("Random Wallpaper")
        self.action_random.triggered.connect(self.wm.fetch_next_wallpaper)

        self.menu.addSeparator()

        # Navigation Actions
        self.action_library = self.menu.addAction("Wallpaper Library")
        self.action_library.triggered.connect(self.open_library_requested.emit)

        self.action_settings = self.menu.addAction("Settings")
        self.action_settings.triggered.connect(self.open_settings_requested.emit)

        self.menu.addSeparator()

        self.action_exit = self.menu.addAction("Exit")
        self.action_exit.triggered.connect(self.exit_requested.emit)

    def update_wallpaper_title(self, meta: dict):
        res = meta.get("resolution", "Unknown")
        wp_id = meta.get("id", "Unknown")
        self.title_action.setText(f"Current: #{wp_id} ({res})")

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.open_main_requested.emit()
