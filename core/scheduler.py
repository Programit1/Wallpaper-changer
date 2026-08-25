"""
Wallpaper Rotation Scheduler.
Uses lightweight QTimer to trigger wallpaper changes at configured intervals.
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

INTERVAL_MAP_MS = {
    "5 Mins": 5 * 60 * 1000,
    "15 Mins": 15 * 60 * 1000,
    "30 Mins": 30 * 60 * 1000,
    "1 Hour": 60 * 60 * 1000,
    "3 Hours": 3 * 60 * 60 * 1000,
    "6 Hours": 6 * 60 * 60 * 1000,
    "Daily": 24 * 60 * 60 * 1000,
    "Manual": 0
}


class WallpaperScheduler(QObject):
    """Event-driven scheduler for automatic wallpaper rotation."""
    rotation_triggered = pyqtSignal()

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timeout)
        self.update_interval()

    def update_interval(self):
        interval_str = self.config.get("rotation_interval", "1 Hour")
        ms = INTERVAL_MAP_MS.get(interval_str, 3600000)
        self.timer.stop()
        if ms > 0:
            self.timer.start(ms)
            print(f"Wallpaper rotation scheduler updated to: {interval_str} ({ms}ms)")
        else:
            print("Wallpaper rotation scheduler disabled (Manual mode).")

    def _on_timeout(self):
        print("Wallpaper rotation scheduler triggered automatic change.")
        self.rotation_triggered.emit()

    def trigger_now(self):
        self.rotation_triggered.emit()
