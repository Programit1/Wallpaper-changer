"""
Main Application Dashboard UI.
Displays current wallpaper preview, metadata details, action controls, and tabs.
"""

import os
import subprocess
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTabWidget, QStatusBar, QFrame
)
from PyQt6.QtGui import QPixmap
from ui.library_view import LibraryView
from ui.settings_view import SettingsDialog


class MainWindow(QMainWindow):
    """Main Dashboard Window."""

    def __init__(self, wallpaper_manager, config_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.config = config_manager
        self.tray_icon_ref = None

        self.setWindowTitle("Wallhaven Wallpaper Changer")
        self.setMinimumSize(820, 520)
        self.resize(880, 560)

        self._init_ui()
        self.update_current_display(self.wm.current_wallpaper)

        # Connect Signals
        self.wm.wallpaper_changed.connect(self.update_current_display)
        self.wm.status_message.connect(self.statusBar().showMessage)

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)

        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # Dashboard Tab
        dash_tab = QWidget()
        dash_layout = QHBoxLayout(dash_tab)
        dash_layout.setContentsMargins(14, 14, 14, 14)
        dash_layout.setSpacing(16)

        # Left Column: Wallpaper Preview Card
        left_card = QFrame(self)
        left_card.setObjectName("CardPanel")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(10, 10, 10, 10)

        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            background-color: #020617;
            border: 1px solid #1e293b;
            border-radius: 6px;
        """)
        self.preview_label.setMinimumSize(460, 300)
        left_layout.addWidget(self.preview_label, 1)

        dash_layout.addWidget(left_card, 3)

        # Right Column: Details & Action Panel
        right_card = QFrame(self)
        right_card.setObjectName("CardPanel")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(14)

        # Header Title
        self.lbl_title = QLabel("Wallpaper: Loading...", self)
        self.lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        right_layout.addWidget(self.lbl_title)

        # Details Grid
        details_layout = QVBoxLayout()
        details_layout.setSpacing(6)

        self.lbl_resolution = QLabel("Resolution: ---", self)
        self.lbl_resolution.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        details_layout.addWidget(self.lbl_resolution)

        self.lbl_source = QLabel("Source: Wallhaven", self)
        self.lbl_source.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.lbl_source.setWordWrap(True)
        details_layout.addWidget(self.lbl_source)

        right_layout.addLayout(details_layout)

        # Primary Actions (Change Now, Next, Favorite)
        actions_box = QVBoxLayout()
        actions_box.setSpacing(8)

        self.btn_change = QPushButton("Fetch New Wallpaper", self)
        self.btn_change.setObjectName("PrimaryButton")
        self.btn_change.clicked.connect(self.wm.fetch_next_wallpaper)
        actions_box.addWidget(self.btn_change)

        sub_btns = QHBoxLayout()
        self.btn_next = QPushButton("Next in History", self)
        self.btn_next.clicked.connect(self.wm.fetch_next_in_history)
        sub_btns.addWidget(self.btn_next)

        self.btn_favorite = QPushButton("Favorite", self)
        self.btn_favorite.clicked.connect(self._toggle_favorite)
        sub_btns.addWidget(self.btn_favorite)
        actions_box.addLayout(sub_btns)

        right_layout.addLayout(actions_box)

        # Auto Rotation Control
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Auto Rotation:", self))
        self.combo_interval = QComboBox(self)
        self.combo_interval.addItems(["5 Mins", "15 Mins", "30 Mins", "1 Hour", "3 Hours", "6 Hours", "Daily", "Manual"])
        self.combo_interval.setCurrentText(self.config.get("rotation_interval", "1 Hour"))
        self.combo_interval.currentTextChanged.connect(self._on_interval_changed)
        interval_layout.addWidget(self.combo_interval)
        right_layout.addLayout(interval_layout)

        # Bottom Utilities
        right_layout.addStretch()

        utils_layout = QHBoxLayout()
        self.btn_open_file = QPushButton("Open File Folder", self)
        self.btn_open_file.clicked.connect(self._open_wallpaper_folder)
        utils_layout.addWidget(self.btn_open_file)

        self.btn_open_settings = QPushButton("Settings", self)
        self.btn_open_settings.clicked.connect(self.open_settings)
        utils_layout.addWidget(self.btn_open_settings)

        right_layout.addLayout(utils_layout)

        dash_layout.addWidget(right_card, 2)

        self.tab_widget.addTab(dash_tab, "Dashboard")

        # Library Tab
        self.library_view = LibraryView(self.wm, self)
        self.tab_widget.addTab(self.library_view, "Wallpaper Library")

        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")

    def update_current_display(self, meta: dict | None):
        if not meta:
            self.lbl_title.setText("Wallpaper: None Selected")
            self.lbl_resolution.setText("Resolution: ---")
            self.lbl_source.setText("Source: Wallhaven")
            self.preview_label.setText("No wallpaper loaded")
            return

        wp_id = meta.get("id", "Unknown")
        res = meta.get("resolution", "Unknown")
        is_fav = meta.get("favorite", False)
        source = meta.get("source_url", "Wallhaven")

        fav_symbol = "★ " if is_fav else ""
        self.lbl_title.setText(f"{fav_symbol}Wallpaper #{wp_id}")
        self.lbl_resolution.setText(f"Resolution: {res}")
        self.lbl_source.setText(f"Source: {source}")

        if is_fav:
            self.btn_favorite.setText("★ Favorited")
            self.btn_favorite.setObjectName("FavoriteButton")
        else:
            self.btn_favorite.setText("Favorite")
            self.btn_favorite.setObjectName("")
        self.btn_favorite.setStyle(self.btn_favorite.style())

        # Update Preview Image
        thumb_path = meta.get("thumb_path")
        filepath = meta.get("filepath")
        target_img = thumb_path if (thumb_path and os.path.exists(thumb_path)) else filepath

        if target_img and os.path.exists(target_img):
            pixmap = QPixmap(target_img)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
            else:
                self.preview_label.setText("Preview unavailable")
        else:
            self.preview_label.setText("Preview unavailable")

    def _toggle_favorite(self):
        fav = self.wm.toggle_current_favorite()
        if fav:
            self.btn_favorite.setText("★ Favorited")
            self.btn_favorite.setObjectName("FavoriteButton")
        else:
            self.btn_favorite.setText("Favorite")
            self.btn_favorite.setObjectName("")
        self.btn_favorite.setStyle(self.btn_favorite.style())

    def _open_wallpaper_folder(self):
        if self.wm.current_wallpaper:
            fpath = self.wm.current_wallpaper.get("filepath")
            if fpath and os.path.exists(fpath):
                subprocess.Popen(f'explorer /select,"{os.path.abspath(fpath)}"')

    def _on_interval_changed(self, interval_str: str):
        self.config.set("rotation_interval", interval_str)
        self.wm.scheduler.update_interval()

    def _on_tab_changed(self, index: int):
        if index == 1:
            self.library_view.reload_library()

    def open_settings(self):
        dialog = SettingsDialog(self.config, self.wm, self)
        if dialog.exec():
            self.combo_interval.setCurrentText(self.config.get("rotation_interval", "1 Hour"))
            self.library_view.reload_library()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.wm.current_wallpaper:
            self.update_current_display(self.wm.current_wallpaper)

    def closeEvent(self, event):
        """Intersects window close button: hides window to system tray instead of exiting app."""
        if self.tray_icon_ref and self.tray_icon_ref.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def set_tray_ref(self, tray_icon):
        self.tray_icon_ref = tray_icon
