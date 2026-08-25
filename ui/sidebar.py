"""
Compact Pinterest-style Sidebar Navigation.
Clean visual hierarchy with Discover, Categories, Library, and Settings.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QWidget
)
from config import GENRES


class SidebarWidget(QFrame):
    """Compact Navigation Sidebar."""

    nav_selected = pyqtSignal(str, str)  # (section_type, value)

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setObjectName("SidebarFrame")
        self.setFixedWidth(200)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(6)

        # Header Title
        header = QLabel("WALLPAPER CHANGER", self)
        header.setObjectName("SidebarHeader")
        layout.addWidget(header)

        # Main List Widget
        self.nav_list = QListWidget(self)
        self.nav_list.setObjectName("SidebarList")
        self.nav_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 1. Discover Section
        item_discover = QListWidgetItem("🔥 Discover")
        item_discover.setData(Qt.ItemDataRole.UserRole, ("discover", "Random"))
        self.nav_list.addItem(item_discover)

        # 2. Categories Header
        cat_hdr = QListWidgetItem("CATEGORIES")
        cat_hdr.setFlags(Qt.ItemFlag.NoItemFlags)
        cat_hdr.setForeground(Qt.GlobalColor.gray)
        self.nav_list.addItem(cat_hdr)

        current_genre = self.config.get("selected_genre", "Cyberpunk")
        selected_item = item_discover

        for genre in GENRES:
            if genre.lower() == "random":
                continue
            item = QListWidgetItem(f"   {genre}")
            item.setData(Qt.ItemDataRole.UserRole, ("category", genre))
            self.nav_list.addItem(item)
            if genre.lower() == current_genre.lower():
                selected_item = item

        # 3. Library Section
        lib_hdr = QListWidgetItem("LIBRARY")
        lib_hdr.setFlags(Qt.ItemFlag.NoItemFlags)
        self.nav_list.addItem(lib_hdr)

        item_fav = QListWidgetItem("★ Favorites")
        item_fav.setData(Qt.ItemDataRole.UserRole, ("library", "favorites"))
        self.nav_list.addItem(item_fav)

        item_dl = QListWidgetItem("📁 Downloads")
        item_dl.setData(Qt.ItemDataRole.UserRole, ("library", "downloads"))
        self.nav_list.addItem(item_dl)

        self.nav_list.setCurrentItem(selected_item)
        self.nav_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.nav_list, 1)

        # 4. Settings Button at Bottom
        self.btn_settings = QPushButton("⚙ Settings", self)
        self.btn_settings.clicked.connect(lambda: self.nav_selected.emit("settings", ""))
        layout.addWidget(self.btn_settings)

    def _on_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            sec_type, val = data
            if sec_type == "category":
                self.config.set("selected_genre", val)
                self.config.set("custom_search", "")
            self.nav_selected.emit(sec_type, val)

    def select_item(self, sec_type: str, val: str = ""):
        for i in range(self.nav_list.count()):
            item = self.nav_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and data[0] == sec_type and (not val or data[1].lower() == val.lower()):
                self.nav_list.setCurrentItem(item)
                break
