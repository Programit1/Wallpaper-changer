"""
Main Pinterest-style Wallpaper Discovery Window.
Integrates top search bar, sidebar navigation, masonry gallery feed, favorites, and settings.
"""

import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QStackedWidget, QStatusBar, QFrame
)
from PyQt6.QtGui import QPixmap
from ui.sidebar import SidebarWidget
from ui.masonry_gallery import MasonryGallery
from ui.settings_view import SettingsDialog


class MainWindow(QMainWindow):
    """Main Application Window."""

    def __init__(self, wallpaper_manager, config_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.config = config_manager
        self.tray_icon_ref = None
        self.current_page = 1
        self.active_query = ""

        self.setWindowTitle("Wallhaven Wallpaper Changer")
        self.setMinimumSize(980, 620)
        self.resize(1120, 680)

        self._init_ui()
        self.update_current_display(self.wm.current_wallpaper)

        # Connect Signals
        self.wm.wallpaper_changed.connect(self.update_current_display)
        self.wm.status_message.connect(self.statusBar().showMessage)

        # Trigger initial search feed
        initial_genre = self.config.get("selected_genre", "Cyberpunk")
        self._fetch_online_feed(initial_genre, page=1, append=False)

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Sidebar Navigation
        self.sidebar = SidebarWidget(self.config, self)
        self.sidebar.nav_selected.connect(self._on_sidebar_nav)
        main_layout.addWidget(self.sidebar)

        # Right Main Content Section
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(16, 12, 16, 12)
        right_layout.setSpacing(12)

        # Top Bar: Search Bar & Current Wallpaper Status
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        # Search Bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("🔍 Search wallpapers... (e.g. dark cyberpunk city)")
        self.search_bar.setText(self.config.get("custom_search", ""))
        self.search_bar.returnPressed.connect(self._on_search_submitted)
        top_bar.addWidget(self.search_bar, 1)

        # Compact Desktop Status Pill
        self.status_pill = QFrame(self)
        self.status_pill.setStyleSheet("""
            QFrame {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 18px;
                padding: 2px 10px;
            }
        """)
        pill_layout = QHBoxLayout(self.status_pill)
        pill_layout.setContentsMargins(8, 4, 8, 4)
        pill_layout.setSpacing(8)

        self.pill_thumb = QLabel(self.status_pill)
        self.pill_thumb.setFixedSize(28, 20)
        self.pill_thumb.setStyleSheet("border-radius: 3px; background-color: #020617;")
        pill_layout.addWidget(self.pill_thumb)

        self.pill_text = QLabel("Desktop: None", self.status_pill)
        self.pill_text.setStyleSheet("font-size: 12px; color: #94a3b8; font-weight: 500;")
        pill_layout.addWidget(self.pill_text)

        top_bar.addWidget(self.status_pill)

        right_layout.addLayout(top_bar)

        # Stacked Pages
        self.stack = QStackedWidget(self)

        # Page 0: Online Masonry Gallery
        self.discover_gallery = MasonryGallery(self.wm, self.config, self)
        self.discover_gallery.load_more_requested.connect(self._on_load_more_requested)
        self.stack.addWidget(self.discover_gallery)

        # Page 1: Favorites Masonry Gallery
        self.fav_gallery = MasonryGallery(self.wm, self.config, self)
        self.stack.addWidget(self.fav_gallery)

        # Page 2: Downloads Masonry Gallery
        self.downloads_gallery = MasonryGallery(self.wm, self.config, self)
        self.stack.addWidget(self.downloads_gallery)

        right_layout.addWidget(self.stack, 1)

        main_layout.addWidget(right_widget, 1)

        # Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")

    def _fetch_online_feed(self, query: str = "", page: int = 1, append: bool = False):
        """Fetches wallpapers from Wallhaven API and populates discovery masonry feed."""
        self.active_query = query
        self.current_page = page
        self.statusBar().showMessage(f"Fetching wallpapers for '{query or 'Discover'}' (Page {page})...")

        cats = self.config.get_categories_string()
        purity = self.config.get_purity_string()
        sorting = self.config.get("sorting", "random")
        res_param = self.config.get_resolution_param()

        res_data = self.wm.api_client.search_wallpapers(
            query=query,
            categories=cats,
            purity=purity,
            sorting=sorting,
            resolutions=res_param,
            page=page
        )

        meta_info = res_data.get("meta", {})
        if meta_info.get("error"):
            self.statusBar().showMessage(f"API Error: {meta_info['error']}")
            return

        items = res_data.get("data", [])
        if not items and not append:
            self.statusBar().showMessage("No wallpapers found for search query.")
            self.discover_gallery.set_items([], append=False, show_load_more=False)
            return

        self.statusBar().showMessage(f"Loaded {len(items)} wallpapers.")
        self.discover_gallery.set_items(items, append=append, show_load_more=True)

    def _on_search_submitted(self):
        query = self.search_bar.text().strip()
        self.config.set("custom_search", query)
        self.stack.setCurrentIndex(0)
        self._fetch_online_feed(query, page=1, append=False)

    def _on_sidebar_nav(self, sec_type: str, val: str):
        if sec_type == "discover":
            self.search_bar.clear()
            self.config.set("custom_search", "")
            self.stack.setCurrentIndex(0)
            self._fetch_online_feed("", page=1, append=False)
        elif sec_type == "category":
            self.search_bar.clear()
            self.config.set("custom_search", "")
            self.stack.setCurrentIndex(0)
            self._fetch_online_feed(val, page=1, append=False)
        elif sec_type == "library":
            if val == "favorites":
                self.stack.setCurrentIndex(1)
                self.load_favorites_feed()
            elif val == "downloads":
                self.stack.setCurrentIndex(2)
                self.load_downloads_feed()
        elif sec_type == "settings":
            self.open_settings()

    def _on_load_more_requested(self):
        self.current_page += 1
        self._fetch_online_feed(self.active_query, page=self.current_page, append=True)

    def load_favorites_feed(self):
        items = list(self.wm.cache_manager.index.values())
        favs = [item for item in items if item.get("favorite", False)]
        self.fav_gallery.set_items(favs, append=False, show_load_more=False)

    def load_downloads_feed(self):
        items = list(self.wm.cache_manager.index.values())
        items.sort(key=lambda x: x.get("download_date", 0), reverse=True)
        self.downloads_gallery.set_items(items, append=False, show_load_more=False)

    def update_current_display(self, meta: dict | None):
        if not meta:
            self.pill_text.setText("Desktop: None")
            return

        wp_id = meta.get("id", "Unknown")
        res = meta.get("resolution", "Unknown")
        self.pill_text.setText(f"Desktop: #{wp_id} [{res}]")

        thumb_path = meta.get("thumb_path")
        filepath = meta.get("filepath")
        target_img = thumb_path if (thumb_path and os.path.exists(thumb_path)) else filepath

        if target_img and os.path.exists(target_img):
            pixmap = QPixmap(target_img)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.pill_thumb.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.pill_thumb.setPixmap(scaled)

    def open_settings(self):
        dialog = SettingsDialog(self.config, self.wm, self)
        if dialog.exec():
            initial_query = self.config.get_active_query()
            self._fetch_online_feed(initial_query, page=1, append=False)

    def closeEvent(self, event):
        """Intersects window close button: hides window to system tray instead of exiting app."""
        if self.tray_icon_ref and self.tray_icon_ref.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def set_tray_ref(self, tray_icon):
        self.tray_icon_ref = tray_icon
