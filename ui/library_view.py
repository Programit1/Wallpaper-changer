"""
Local Wallpaper Library View.
Displays downloaded/cached wallpapers in grid/list view with thumbnails, filtering, and search.
"""

import os
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QFileDialog,
    QMessageBox
)
from PyQt6.QtGui import QIcon


class LibraryView(QWidget):
    """Local Library Widget."""
    wallpaper_selected = pyqtSignal(dict)

    def __init__(self, wallpaper_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.cache_mgr = self.wm.cache_manager

        self._init_ui()
        self.reload_library()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top Bar: Search, Filter, View mode, Import
        top_layout = QHBoxLayout()

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search local library by ID/tag...")
        self.search_input.textChanged.connect(self.filter_library)
        top_layout.addWidget(self.search_input, 2)

        self.filter_combo = QComboBox(self)
        self.filter_combo.addItems(["All", "Favorites", "Recently Used"])
        self.filter_combo.currentIndexChanged.connect(self.filter_library)
        top_layout.addWidget(self.filter_combo, 1)

        self.import_btn = QPushButton("Import Local File", self)
        self.import_btn.clicked.connect(self.import_file)
        top_layout.addWidget(self.import_btn)

        layout.addLayout(top_layout)

        # Wallpaper List / Grid
        self.list_widget = QListWidget(self)
        self.list_widget.setIconSize(QSize(160, 90))
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setSpacing(10)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.list_widget)

        # Bottom Action Bar
        bottom_layout = QHBoxLayout()

        self.info_label = QLabel("0 wallpapers in library", self)
        bottom_layout.addWidget(self.info_label)

        bottom_layout.addStretch()

        self.fav_btn = QPushButton("Favorite", self)
        self.fav_btn.clicked.connect(self._toggle_favorite_selected)
        bottom_layout.addWidget(self.fav_btn)

        self.apply_btn = QPushButton("Set as Wallpaper", self)
        self.apply_btn.setObjectName("PrimaryButton")
        self.apply_btn.clicked.connect(self._apply_selected)
        bottom_layout.addWidget(self.apply_btn)

        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.setObjectName("DangerButton")
        self.delete_btn.clicked.connect(self._delete_selected)
        bottom_layout.addWidget(self.delete_btn)

        layout.addLayout(bottom_layout)

    def reload_library(self):
        """Loads items from cache manager index into list widget."""
        self.list_widget.clear()
        items = list(self.cache_mgr.index.values())

        search = self.search_input.text().lower().strip()
        filter_mode = self.filter_combo.currentText()

        # Apply filters
        filtered = []
        for item in items:
            wp_id = str(item.get("id", "")).lower()
            tags = " ".join(item.get("tags", [])).lower()
            is_fav = item.get("favorite", False)

            if search and (search not in wp_id and search not in tags):
                continue

            if filter_mode == "Favorites" and not is_fav:
                continue

            filtered.append(item)

        if filter_mode == "Recently Used":
            filtered.sort(key=lambda x: x.get("last_used_timestamp", 0), reverse=True)

        for meta in filtered:
            thumb_path = meta.get("thumb_path", "")
            wp_id = meta.get("id", "WP")
            res = meta.get("resolution", "")
            fav_str = "★ " if meta.get("favorite") else ""

            label = f"{fav_str}#{wp_id}\n[{res}]"

            list_item = QListWidgetItem(label)
            list_item.setData(Qt.ItemDataRole.UserRole, meta)

            if os.path.exists(thumb_path):
                list_item.setIcon(QIcon(thumb_path))
            else:
                filepath = meta.get("filepath", "")
                if os.path.exists(filepath):
                    list_item.setIcon(QIcon(filepath))

            self.list_widget.addItem(list_item)

        self.info_label.setText(f"{len(filtered)} wallpapers shown ({len(items)} total)")

    def filter_library(self):
        self.reload_library()

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Wallpaper Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.webp)"
        )
        if file_path:
            meta = self.cache_mgr.add_local_file(file_path)
            if meta:
                self.reload_library()
                QMessageBox.information(self, "Import Successful", f"Imported {os.path.basename(file_path)} into library.")

    def _get_selected_meta(self) -> dict | None:
        current_item = self.list_widget.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None

    def _on_item_double_clicked(self, item: QListWidgetItem):
        meta = item.data(Qt.ItemDataRole.UserRole)
        if meta:
            self.wm.apply_wallpaper_item(meta)

    def _apply_selected(self):
        meta = self._get_selected_meta()
        if meta:
            self.wm.apply_wallpaper_item(meta)

    def _toggle_favorite_selected(self):
        meta = self._get_selected_meta()
        if meta:
            wp_id = meta.get("id")
            fav = self.cache_mgr.toggle_favorite(wp_id)
            meta["favorite"] = fav
            self.reload_library()

    def _delete_selected(self):
        meta = self._get_selected_meta()
        if meta:
            wp_id = meta.get("id")
            confirm = QMessageBox.question(
                self,
                "Delete Wallpaper",
                f"Are you sure you want to delete wallpaper #{wp_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.cache_mgr.delete_wallpaper(wp_id)
                self.reload_library()
