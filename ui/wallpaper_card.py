"""
Reusable Pinterest-style Wallpaper Card Component.
Renders thumbnail image with dynamic height, hover action overlays, and click signals.
"""

import os
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QColor


class WallpaperCard(QWidget):
    """Pinterest-style Wallpaper Image Card with hover overlays."""

    card_clicked = pyqtSignal(dict)
    set_wallpaper_clicked = pyqtSignal(dict)
    favorite_clicked = pyqtSignal(dict)
    download_clicked = pyqtSignal(dict)

    def __init__(self, item_data: dict, wallpaper_manager, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.wm = wallpaper_manager
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._init_ui()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Image Container Frame
        self.container = QWidget(self)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #111827;
                border-radius: 8px;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Image Label
        self.image_label = QLabel(self.container)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border-radius: 8px; background-color: #111827;")
        self.image_label.setScaledContents(True)

        container_layout.addWidget(self.image_label)

        # Dark Hover Overlay Widget
        self.overlay = QWidget(self.container)
        self.overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(9, 13, 22, 0.65);
                border-radius: 8px;
            }
        """)
        self.overlay.hide()

        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(8, 8, 8, 8)

        # Top Overlay Bar (Favorite Button)
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        is_fav = self.item_data.get("favorite", False)
        wp_id = str(self.item_data.get("id"))
        if self.wm.cache_manager.is_cached(wp_id):
            cached_meta = self.wm.cache_manager.get_wallpaper(wp_id)
            if cached_meta:
                is_fav = cached_meta.get("favorite", False)

        fav_str = "★" if is_fav else "☆"
        self.btn_fav = QPushButton(fav_str, self.overlay)
        self.btn_fav.setObjectName("OverlayBtn")
        self.btn_fav.clicked.connect(self._on_favorite_clicked)
        top_bar.addWidget(self.btn_fav)

        overlay_layout.addLayout(top_bar)
        overlay_layout.addStretch()

        # Bottom Overlay Bar (Set Wallpaper & Download Buttons)
        bottom_bar = QHBoxLayout()
        self.btn_set = QPushButton("Set Wallpaper", self.overlay)
        self.btn_set.setObjectName("OverlayBtn")
        self.btn_set.clicked.connect(self._on_set_clicked)
        bottom_bar.addWidget(self.btn_set)

        bottom_bar.addStretch()

        self.btn_dl = QPushButton("↓ Save", self.overlay)
        self.btn_dl.setObjectName("OverlayBtn")
        self.btn_dl.clicked.connect(self._on_download_clicked)
        bottom_bar.addWidget(self.btn_dl)

        overlay_layout.addLayout(bottom_bar)

        self.main_layout.addWidget(self.container)

    def set_pixmap(self, pixmap: QPixmap, target_width: int = 220):
        """Scales pixmap maintaining natural aspect ratio for masonry display."""
        if pixmap.isNull():
            return

        # Calculate proportional height
        aspect = pixmap.height() / pixmap.width() if pixmap.width() > 0 else 0.75
        target_height = int(target_width * aspect)

        # Clamp max height to avoid excessively tall cards
        target_height = min(max(target_height, 120), 400)

        scaled = pixmap.scaled(
            target_width,
            target_height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled)
        self.image_label.setFixedSize(target_width, target_height)
        self.overlay.setFixedSize(target_width, target_height)
        self.setFixedSize(target_width, target_height)

    def enterEvent(self, event):
        self.overlay.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.overlay.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click was on action buttons
            pos = event.position().toPoint()
            child = self.childAt(pos)
            if child in (self.btn_fav, self.btn_set, self.btn_dl):
                super().mousePressEvent(event)
                return
            self.card_clicked.emit(self.item_data)
        super().mousePressEvent(event)

    def _on_set_clicked(self):
        self.set_wallpaper_clicked.emit(self.item_data)

    def _on_favorite_clicked(self):
        self.favorite_clicked.emit(self.item_data)
        wp_id = str(self.item_data.get("id"))
        if self.wm.cache_manager.is_cached(wp_id):
            cached_meta = self.wm.cache_manager.get_wallpaper(wp_id)
            if cached_meta:
                fav = cached_meta.get("favorite", False)
                self.btn_fav.setText("★" if fav else "☆")

    def _on_download_clicked(self):
        self.download_clicked.emit(self.item_data)
