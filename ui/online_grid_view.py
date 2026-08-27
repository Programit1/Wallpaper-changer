"""
Online Wallpaper Grid View Widget.
Fetches search results from Wallhaven API and displays interactive thumbnail cards.
"""

import os
import requests
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRunnable, QThreadPool, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QIcon, QPixmap
from utils.image_utils import generate_thumbnail


class ThumbWorkerSignals(QObject):
    """Signals for thumbnail fetcher worker."""
    thumb_ready = pyqtSignal(str, str)  # (wp_id, thumb_local_path)


class ThumbnailFetcherRunnable(QRunnable):
    """Worker runnable to asynchronously download thumbnail previews using QThreadPool."""

    def __init__(self, wp_id: str, thumb_url: str, cache_dir: str):
        super().__init__()
        self.wp_id = wp_id
        self.thumb_url = thumb_url
        self.cache_dir = cache_dir
        self.signals = ThumbWorkerSignals()
        self.setAutoDelete(True)

    def run(self):
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            local_path = os.path.join(self.cache_dir, f"thumb_{self.wp_id}.jpg")
            if not os.path.exists(local_path):
                resp = requests.get(self.thumb_url, timeout=10)
                if resp.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
            self.signals.thumb_ready.emit(self.wp_id, local_path)
        except Exception as e:
            print(f"Error fetching thumbnail for {self.wp_id}: {e}")


class OnlineGridView(QWidget):
    """Online Wallpaper Thumbnail Grid View."""

    apply_requested = pyqtSignal(dict)  # wallpaper metadata item

    def __init__(self, wallpaper_manager, config_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.config = config_manager

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header Bar
        header_box = QHBoxLayout()
        self.lbl_title = QLabel("Online Wallpapers", self)
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        header_box.addWidget(self.lbl_title)

        header_box.addStretch()

        self.btn_refresh = QPushButton("🔄 Refresh Results", self)
        self.btn_refresh.clicked.connect(self.refresh_search)
        header_box.addWidget(self.btn_refresh)

        layout.addLayout(header_box)

        # Grid View ListWidget
        self.grid_list = QListWidget(self)
        self.grid_list.setIconSize(QSize(200, 120))
        self.grid_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.grid_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.grid_list.setSpacing(12)
        self.grid_list.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.grid_list)

        # Bottom Bar & Status
        bottom_box = QHBoxLayout()
        self.lbl_status = QLabel("Ready", self)
        bottom_box.addWidget(self.lbl_status)

        bottom_box.addStretch()

        self.btn_favorite = QPushButton("Favorite", self)
        self.btn_favorite.clicked.connect(self._toggle_favorite_selected)
        bottom_box.addWidget(self.btn_favorite)

        self.btn_set = QPushButton("Set as Wallpaper", self)
        self.btn_set.setObjectName("PrimaryButton")
        self.btn_set.clicked.connect(self._apply_selected)
        bottom_box.addWidget(self.btn_set)

        layout.addLayout(bottom_box)

    def search_query(self, query: str = ""):
        """Executes search against Wallhaven API and displays results in grid."""
        self.lbl_title.setText(f"Online Wallpapers: '{query or 'Random'}'")
        self.lbl_status.setText("Fetching wallpapers from Wallhaven...")
        self.grid_list.clear()

        cats = self.config.get_categories_string()
        purity = self.config.get_purity_string()
        sorting = self.config.get("sorting", "random")
        res_param = self.config.get_resolution_param()

        res_data = self.wm.api_client.search_wallpapers(
            query=query,
            categories=cats,
            purity=purity,
            sorting=sorting,
            resolutions=res_param
        )

        meta_info = res_data.get("meta", {})
        if meta_info.get("error"):
            self.lbl_status.setText(f"API Error: {meta_info['error']}")
            QMessageBox.warning(self, "API Search Error", f"Could not fetch wallpapers: {meta_info['error']}")
            return

        items = res_data.get("data", [])
        if not items:
            self.lbl_status.setText("No wallpapers found for query.")
            return

        self.lbl_status.setText(f"Found {len(items)} wallpapers.")

        # Populate Grid
        cache_dir = self.config.get("cache_dir")
        thumbs_dir = os.path.join(cache_dir, "thumbnails")

        for item_data in items:
            wp_id = str(item_data.get("id"))
            res = item_data.get("resolution", "1920x1080")
            thumbs = item_data.get("thumbs", {})
            thumb_url = thumbs.get("small") or thumbs.get("original") or item_data.get("path", "")

            label_text = f"#{wp_id}\n[{res}]"
            list_item = QListWidgetItem(label_text)

            list_item.setData(Qt.ItemDataRole.UserRole, item_data)
            self.grid_list.addItem(list_item)

            # Fetch thumbnail asynchronously using QThreadPool
            runnable = ThumbnailFetcherRunnable(wp_id, thumb_url, thumbs_dir)
            runnable.signals.thumb_ready.connect(self._on_thumb_ready)
            QThreadPool.globalInstance().start(runnable)

    def refresh_search(self):
        query = self.config.get_active_query()
        self.search_query(query)

    def _on_thumb_ready(self, wp_id: str, thumb_local_path: str):
        for i in range(self.grid_list.count()):
            item = self.grid_list.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)
            if item_data and str(item_data.get("id")) == wp_id:
                if os.path.exists(thumb_local_path):
                    item.setIcon(QIcon(thumb_local_path))
                break

    def _get_selected_data(self) -> dict | None:
        curr = self.grid_list.currentItem()
        if curr:
            return curr.data(Qt.ItemDataRole.UserRole)
        return None

    def _on_item_double_clicked(self, item: QListWidgetItem):
        item_data = item.data(Qt.ItemDataRole.UserRole)
        if item_data:
            self.wm.cache_manager.download_wallpaper(item_data)

    def _apply_selected(self):
        item_data = self._get_selected_data()
        if item_data:
            self.lbl_status.setText("Downloading and applying wallpaper...")
            self.wm.cache_manager.download_wallpaper(item_data)

    def _toggle_favorite_selected(self):
        item_data = self._get_selected_data()
        if item_data:
            wp_id = str(item_data.get("id"))
            if self.wm.cache_manager.is_cached(wp_id):
                fav = self.wm.cache_manager.toggle_favorite(wp_id)
                status = "Favorited" if fav else "Unfavorited"
                self.lbl_status.setText(f"Wallpaper #{wp_id} {status}")
            else:
                self.wm.cache_manager.download_wallpaper(item_data)
                self.wm.cache_manager.toggle_favorite(wp_id)
