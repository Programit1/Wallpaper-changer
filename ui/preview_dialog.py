"""
Lightbox Media Viewer Preview Dialog.
Shows large full-resolution wallpaper preview, metadata, and desktop action buttons.
"""

import os
import subprocess
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QDesktopServices


class PreviewDialog(QDialog):
    """Lightbox Wallpaper Preview Dialog."""

    def __init__(self, item_data: dict, wallpaper_manager, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.wm = wallpaper_manager

        self.setWindowTitle("Wallpaper Preview")
        self.setMinimumSize(840, 560)
        self.resize(960, 640)

        self._init_ui()
        self._load_preview()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Image Viewer Container
        self.image_container = QFrame(self)
        self.image_container.setStyleSheet("background-color: #020617; border-radius: 8px;")
        container_layout = QVBoxLayout(self.image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel(self.image_container)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.preview_label, 1)

        main_layout.addWidget(self.image_container, 1)

        # Bottom Metadata & Actions Toolbar
        bottom_bar = QFrame(self)
        bottom_bar.setObjectName("CardPanel")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(14, 10, 14, 10)
        bottom_layout.setSpacing(12)

        # Details Labels
        wp_id = str(self.item_data.get("id", "Unknown"))
        res = self.item_data.get("resolution", "Unknown")

        details_box = QVBoxLayout()
        details_box.setSpacing(2)

        self.lbl_title = QLabel(f"Wallpaper #{wp_id}", self)
        self.lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        details_box.addWidget(self.lbl_title)

        self.lbl_info = QLabel(f"{res} • Wallhaven", self)
        self.lbl_info.setStyleSheet("font-size: 12px; color: #94a3b8;")
        details_box.addWidget(self.lbl_info)

        bottom_layout.addLayout(details_box, 1)

        # Action Buttons
        self.btn_fav = QPushButton("★ Favorite", self)
        self.btn_fav.clicked.connect(self._toggle_favorite)
        bottom_layout.addWidget(self.btn_fav)

        self.btn_download = QPushButton("↓ Download", self)
        self.btn_download.clicked.connect(self._download_wallpaper)
        bottom_layout.addWidget(self.btn_download)

        self.btn_source = QPushButton("🌐 Source Link", self)
        self.btn_source.clicked.connect(self._open_source_url)
        bottom_layout.addWidget(self.btn_source)

        self.btn_set = QPushButton("Set Desktop Wallpaper", self)
        self.btn_set.setObjectName("PrimaryButton")
        self.btn_set.clicked.connect(self._set_as_wallpaper)
        bottom_layout.addWidget(self.btn_set)

        self.btn_close = QPushButton("Close", self)
        self.btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_close)

        main_layout.addWidget(bottom_bar)

        self._update_fav_button_state()

    def _load_preview(self):
        """Loads preview image asynchronously or from local cache."""
        wp_id = str(self.item_data.get("id"))
        filepath = self.item_data.get("filepath")
        thumb_path = self.item_data.get("thumb_path")

        if self.wm.cache_manager.is_cached(wp_id):
            cached_meta = self.wm.cache_manager.get_wallpaper(wp_id)
            if cached_meta and os.path.exists(cached_meta.get("filepath", "")):
                filepath = cached_meta["filepath"]

        target_path = filepath if (filepath and os.path.exists(filepath)) else thumb_path

        if target_path and os.path.exists(target_path):
            pixmap = QPixmap(target_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)

    def _update_fav_button_state(self):
        wp_id = str(self.item_data.get("id"))
        is_fav = False
        if self.wm.cache_manager.is_cached(wp_id):
            cached_meta = self.wm.cache_manager.get_wallpaper(wp_id)
            if cached_meta:
                is_fav = cached_meta.get("favorite", False)

        if is_fav:
            self.btn_fav.setText("★ Favorited")
            self.btn_fav.setObjectName("FavoriteButton")
        else:
            self.btn_fav.setText("★ Favorite")
            self.btn_fav.setObjectName("")
        self.btn_fav.setStyle(self.btn_fav.style())

    def _toggle_favorite(self):
        wp_id = str(self.item_data.get("id"))
        if not self.wm.cache_manager.is_cached(wp_id):
            self.wm.cache_manager.download_wallpaper(self.item_data)
        self.wm.cache_manager.toggle_favorite(wp_id)
        self._update_fav_button_state()

    def _set_as_wallpaper(self):
        wp_id = str(self.item_data.get("id"))
        if self.wm.cache_manager.is_cached(wp_id):
            meta = self.wm.cache_manager.get_wallpaper(wp_id)
            self.wm.apply_wallpaper_item(meta)
        else:
            self.wm.cache_manager.download_wallpaper(self.item_data)
        self.accept()

    def _download_wallpaper(self):
        wp_id = str(self.item_data.get("id"))
        if not self.wm.cache_manager.is_cached(wp_id):
            self.wm.cache_manager.download_wallpaper(self.item_data)
        
        cached_meta = self.wm.cache_manager.get_wallpaper(wp_id)
        if cached_meta and os.path.exists(cached_meta.get("filepath", "")):
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Wallpaper Image", f"wallpaper_{wp_id}.jpg", "Images (*.jpg *.png)"
            )
            if save_path:
                import shutil
                shutil.copy2(cached_meta["filepath"], save_path)
                QMessageBox.information(self, "Download Complete", f"Saved wallpaper to {save_path}")

    def _open_source_url(self):
        url_str = self.item_data.get("wallhaven_url") or self.item_data.get("path")
        if url_str:
            QDesktopServices.openUrl(QUrl(url_str))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._load_preview()
