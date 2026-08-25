"""
Monitor and Display Manager.
Detects screen resolutions, aspect ratios, and geometries using PyQt6 QGuiApplication.
"""

from PyQt6.QtGui import QGuiApplication, QScreen
from PyQt6.QtCore import QRect
from utils.image_utils import calculate_aspect_ratio


class MonitorManager:
    """Detects active displays, geometry, and resolutions."""

    @staticmethod
    def get_primary_screen() -> QScreen | None:
        return QGuiApplication.primaryScreen()

    @staticmethod
    def get_primary_geometry() -> QRect:
        screen = QGuiApplication.primaryScreen()
        if screen:
            return screen.geometry()
        return QRect(0, 0, 1920, 1080)

    @staticmethod
    def get_primary_resolution_str() -> str:
        geom = MonitorManager.get_primary_geometry()
        return f"{geom.width()}x{geom.height()}"

    @staticmethod
    def get_primary_aspect_ratio_str() -> str:
        geom = MonitorManager.get_primary_geometry()
        return calculate_aspect_ratio(geom.width(), geom.height())

    @staticmethod
    def get_all_screens() -> list[QScreen]:
        return QGuiApplication.screens()
