"""
Masonry Gallery Component.
Multi-column responsive Pinterest-style layout displaying WallpaperCards with dynamic aspect ratio heights.
"""

import os
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QThreadPool
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton,
    QFrame
)
from PyQt6.QtGui import QPixmap
from ui.wallpaper_card import WallpaperCard
from ui.preview_dialog import PreviewDialog
from ui.online_grid_view import ThumbnailFetcherRunnable


class MasonryGallery(QWidget):
    """Responsive Pinterest-style Masonry Gallery Widget."""

    load_more_requested = pyqtSignal()

    def __init__(self, wallpaper_manager, config_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.config = config_manager
        self.items_data: list[dict] = []
        self.cards: list[WallpaperCard] = []

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("MasonryScroll")
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget(self.scroll_area)
        self.container.setObjectName("MasonryContainer")

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 12, 12, 12)
        self.container_layout.setSpacing(12)

        # Columns Layout Frame
        self.cols_widget = QWidget(self.container)
        self.cols_layout = QHBoxLayout(self.cols_widget)
        self.cols_layout.setContentsMargins(0, 0, 0, 0)
        self.cols_layout.setSpacing(12)

        self.container_layout.addWidget(self.cols_widget)

        # Load More Button Bar
        self.load_more_bar = QHBoxLayout()
        self.load_more_bar.addStretch()

        self.btn_load_more = QPushButton("Load More Wallpapers", self.container)
        self.btn_load_more.clicked.connect(self.load_more_requested.emit)
        self.btn_load_more.hide()
        self.load_more_bar.addWidget(self.btn_load_more)

        self.load_more_bar.addStretch()
        self.container_layout.addLayout(self.load_more_bar)

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

    def set_items(self, items: list[dict], append: bool = False, show_load_more: bool = True):
        """Sets or appends wallpaper items to the masonry grid."""
        if not append:
            self.items_data = list(items)
            self._rebuild_grid()
        else:
            new_items = list(items)
            self.items_data.extend(new_items)
            self._rebuild_grid()

        if show_load_more and len(self.items_data) > 0:
            self.btn_load_more.show()
        else:
            self.btn_load_more.hide()

    def _get_column_count(self) -> int:
        width = self.width()
        if width < 750:
            return 2
        elif width < 1050:
            return 3
        else:
            return 4

    def _rebuild_grid(self):
        """Rebuilds the masonry multi-column structure."""
        while self.cols_layout.count() > 0:
            child = self.cols_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.items_data:
            empty_lbl = QLabel("No wallpapers found.", self.cols_widget)
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
            self.cols_layout.addWidget(empty_lbl)
            return

        num_cols = self._get_column_count()
        column_widgets = []
        column_layouts = []

        for i in range(num_cols):
            col_w = QWidget(self.cols_widget)
            col_l = QVBoxLayout(col_w)
            col_l.setContentsMargins(0, 0, 0, 0)
            col_l.setSpacing(12)
            col_l.addStretch()
            self.cols_layout.addWidget(col_w)
            column_widgets.append(col_w)
            column_layouts.append(col_l)

        card_width = max(int((self.width() - (num_cols * 16) - 40) / num_cols), 180)

        for i, item_data in enumerate(self.items_data):
            col_idx = i % num_cols
            card = WallpaperCard(item_data, self.wm, column_widgets[col_idx])
            
            card.card_clicked.connect(self._on_card_clicked)
            card.set_wallpaper_clicked.connect(self._on_card_set_wallpaper)
            card.favorite_clicked.connect(self._on_card_favorite)
            card.download_clicked.connect(self._on_card_download)

            self._load_card_pixmap(card, item_data, card_width)

            target_layout = column_layouts[col_idx]
            target_layout.insertWidget(target_layout.count() - 1, card)

    def _load_card_pixmap(self, card: WallpaperCard, item_data: dict, card_width: int):
        wp_id = str(item_data.get("id"))
        thumb_path = item_data.get("thumb_path")
        filepath = item_data.get("filepath")

        if self.wm.cache_manager.is_cached(wp_id):
            cached_meta = self.wm.cache_manager.get_wallpaper(wp_id)
            if cached_meta and os.path.exists(cached_meta.get("thumb_path", "")):
                thumb_path = cached_meta["thumb_path"]

        target_img = thumb_path if (thumb_path and os.path.exists(thumb_path)) else filepath

        if target_img and os.path.exists(target_img):
            pixmap = QPixmap(target_img)
            if not pixmap.isNull():
                card.set_pixmap(pixmap, target_width=card_width)
            else:
                card.set_pixmap(QPixmap(card_width, int(card_width * 0.75)), target_width=card_width)
        else:
            thumbs = item_data.get("thumbs", {})
            thumb_url = thumbs.get("small") or thumbs.get("original") or item_data.get("path", "")
            if thumb_url:
                cache_dir = self.config.get("cache_dir")
                thumbs_dir = os.path.join(cache_dir, "thumbnails")
                runnable = ThumbnailFetcherRunnable(wp_id, thumb_url, thumbs_dir)
                
                def make_on_ready(c, w_id, w_w):
                    def on_ready(fetched_id, local_path):
                        if fetched_id == w_id and os.path.exists(local_path):
                            px = QPixmap(local_path)
                            c.set_pixmap(px, target_width=w_w)
                    return on_ready

                runnable.signals.thumb_ready.connect(make_on_ready(card, wp_id, card_width))
                QThreadPool.globalInstance().start(runnable)

    def _on_card_clicked(self, item_data: dict):
        preview = PreviewDialog(item_data, self.wm, self)
        preview.exec()

    def _on_card_set_wallpaper(self, item_data: dict):
        wp_id = str(item_data.get("id"))
        if self.wm.cache_manager.is_cached(wp_id):
            meta = self.wm.cache_manager.get_wallpaper(wp_id)
            self.wm.apply_wallpaper_item(meta)
        else:
            self.wm.cache_manager.download_wallpaper(item_data)

    def _on_card_favorite(self, item_data: dict):
        wp_id = str(item_data.get("id"))
        if not self.wm.cache_manager.is_cached(wp_id):
            self.wm.cache_manager.download_wallpaper(item_data)
        self.wm.cache_manager.toggle_favorite(wp_id)

    def _on_card_download(self, item_data: dict):
        wp_id = str(item_data.get("id"))
        if not self.wm.cache_manager.is_cached(wp_id):
            self.wm.cache_manager.download_wallpaper(item_data)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.items_data:
            self._rebuild_grid()
