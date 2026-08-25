"""
Main Dashboard UI with Sidebar Navigation, Online Grid Browser, Favorites, and Local Library.
"""

import os
import subprocess
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QStackedWidget, QStatusBar, QFrame
)
from PyQt6.QtGui import QPixmap
from ui.sidebar import SidebarWidget
from ui.online_grid_view import OnlineGridView
from ui.library_view import LibraryView
from ui.settings_view import SettingsDialog


class MainWindow(QMainWindow):
    """Main Application Window."""

    def __init__(self, wallpaper_manager, config_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.config = config_manager
        self.tray_icon_ref = None

        self.setWindowTitle("Wallhaven Wallpaper Changer")
        self.setMinimumSize(960, 600)
        self.resize(1040, 640)

        self._init_ui()
        self.update_current_display(self.wm.current_wallpaper)

        # Connect Signals
        self.wm.wallpaper_changed.connect(self.update_current_display)
        self.wm.status_message.connect(self.statusBar().showMessage)

        # Trigger initial search on startup
        initial_query = self.config.get_active_query()
        self.online_grid.search_query(initial_query)

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Left Sidebar Navigation Panel
        self.sidebar = SidebarWidget(self.config, self)
        self.sidebar.genre_selected.connect(self._on_genre_selected)
        self.sidebar.search_submitted.connect(self._on_search_submitted)
        self.sidebar.nav_changed.connect(self._on_nav_changed)
        main_layout.addWidget(self.sidebar)

        # Divider Line
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("color: #334155;")
        main_layout.addWidget(line)

        # Right Main Content Container
        right_container = QVBoxLayout()
        right_container.setContentsMargins(6, 6, 6, 6)
        right_container.setSpacing(10)

        # Active Wallpaper Header Banner
        active_card = QFrame(self)
        active_card.setObjectName("CardPanel")
        active_layout = QHBoxLayout(active_card)
        active_layout.setContentsMargins(10, 8, 10, 8)
        active_layout.setSpacing(12)

        self.active_thumb_lbl = QLabel(self)
        self.active_thumb_lbl.setFixedSize(90, 54)
        self.active_thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_thumb_lbl.setStyleSheet("""
            background-color: #020617;
            border: 1px solid #334155;
            border-radius: 4px;
        """)
        active_layout.addWidget(self.active_thumb_lbl)

        info_box = QVBoxLayout()
        info_box.setSpacing(2)

        self.lbl_title = QLabel("Current: None Loaded", self)
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        info_box.addWidget(self.lbl_title)

        self.lbl_details = QLabel("Resolution: --- | Category: ---", self)
        self.lbl_details.setStyleSheet("font-size: 12px; color: #94a3b8;")
        info_box.addWidget(self.lbl_details)

        active_layout.addLayout(info_box, 1)

        # Quick Control Buttons
        self.btn_favorite = QPushButton("★ Favorite", self)
        self.btn_favorite.clicked.connect(self._toggle_favorite)
        active_layout.addWidget(self.btn_favorite)

        self.btn_next = QPushButton("Next Wallpaper", self)
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.clicked.connect(self.wm.fetch_next_wallpaper)
        active_layout.addWidget(self.btn_next)

        right_container.addWidget(active_card)

        # Stacked Pages Widget
        self.stack = QStackedWidget(self)

        # Page 0: Online Grid View
        self.online_grid = OnlineGridView(self.wm, self.config, self)
        self.stack.addWidget(self.online_grid)

        # Page 1: Favorites View
        self.fav_library = LibraryView(self.wm, self)
        self.fav_library.filter_combo.setCurrentText("Favorites")
        self.stack.addWidget(self.fav_library)

        # Page 2: Local Library View
        self.local_library = LibraryView(self.wm, self)
        self.stack.addWidget(self.local_library)

        right_container.addWidget(self.stack, 1)

        main_layout.addLayout(right_container, 1)

        # Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")

    def _on_genre_selected(self, genre: str):
        self.stack.setCurrentIndex(0)
        self.online_grid.search_query(genre)

    def _on_search_submitted(self, query: str):
        self.stack.setCurrentIndex(0)
        self.online_grid.search_query(query)

    def _on_nav_changed(self, page_index: int):
        if page_index == 3:  # Settings
            self.open_settings()
        else:
            self.stack.setCurrentIndex(page_index)
            if page_index == 1:
                self.fav_library.filter_combo.setCurrentText("Favorites")
                self.fav_library.reload_library()
            elif page_index == 2:
                self.local_library.filter_combo.setCurrentText("All")
                self.local_library.reload_library()

    def update_current_display(self, meta: dict | None):
        if not meta:
            self.lbl_title.setText("Current: None Loaded")
            self.lbl_details.setText("Resolution: ---")
            self.active_thumb_lbl.setText("No Image")
            return

        wp_id = meta.get("id", "Unknown")
        res = meta.get("resolution", "Unknown")
        is_fav = meta.get("favorite", False)
        genre = self.config.get("selected_genre", "Cyberpunk")

        fav_symbol = "★ " if is_fav else ""
        self.lbl_title.setText(f"{fav_symbol}Current: Wallpaper #{wp_id}")
        self.lbl_details.setText(f"Resolution: {res} | Category: {genre}")

        if is_fav:
            self.btn_favorite.setText("★ Favorited")
            self.btn_favorite.setObjectName("FavoriteButton")
        else:
            self.btn_favorite.setText("★ Favorite")
            self.btn_favorite.setObjectName("")
        self.btn_favorite.setStyle(self.btn_favorite.style())

        # Update Thumbnail
        thumb_path = meta.get("thumb_path")
        filepath = meta.get("filepath")
        target_img = thumb_path if (thumb_path and os.path.exists(thumb_path)) else filepath

        if target_img and os.path.exists(target_img):
            pixmap = QPixmap(target_img)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.active_thumb_lbl.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.active_thumb_lbl.setPixmap(scaled)

    def _toggle_favorite(self):
        fav = self.wm.toggle_current_favorite()
        if fav:
            self.btn_favorite.setText("★ Favorited")
            self.btn_favorite.setObjectName("FavoriteButton")
        else:
            self.btn_favorite.setText("★ Favorite")
            self.btn_favorite.setObjectName("")
        self.btn_favorite.setStyle(self.btn_favorite.style())

    def open_settings(self):
        dialog = SettingsDialog(self.config, self.wm, self)
        if dialog.exec():
            self.local_library.reload_library()
            self.fav_library.reload_library()
            self.online_grid.refresh_search()

    def closeEvent(self, event):
        """Intersects window close button: hides window to system tray instead of exiting app."""
        if self.tray_icon_ref and self.tray_icon_ref.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def set_tray_ref(self, tray_icon):
        self.tray_icon_ref = tray_icon
