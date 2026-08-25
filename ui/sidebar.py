"""
Left Sidebar Navigation Panel.
Includes Search input, Genre/Category selector, and Quick Navigation buttons.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QFrame
)
from config import GENRES


class SidebarWidget(QWidget):
    """Sidebar Navigation Widget."""

    genre_selected = pyqtSignal(str)
    search_submitted = pyqtSignal(str)
    nav_changed = pyqtSignal(int)  # 0: Browse Grid, 1: Favorites, 2: Library, 3: Settings

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setFixedWidth(210)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(12)

        # App Header
        header = QLabel("🖼 Wallpaper Changer", self)
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8; padding: 4px 2px;")
        layout.addWidget(header)

        # Search Bar
        search_box = QVBoxLayout()
        search_label = QLabel("Custom Search:", self)
        search_label.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: 600;")
        search_box.addWidget(search_label)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("e.g. dark cyberpunk")
        self.search_input.setText(self.config.get("custom_search", ""))
        self.search_input.returnPressed.connect(self._on_search_submitted)
        search_box.addWidget(self.search_input)

        layout.addLayout(search_box)

        # Divider
        line1 = QFrame(self)
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("color: #334155;")
        layout.addWidget(line1)

        # Categories Label
        cat_label = QLabel("CATEGORIES", self)
        cat_label.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: bold;")
        layout.addWidget(cat_label)

        # Genre Category List
        self.genre_list = QListWidget(self)
        self.genre_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
                color: #e2e8f0;
            }
            QListWidget::item:selected {
                background-color: #0284c7;
                color: #ffffff;
                font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background-color: #1e293b;
            }
        """)

        current_genre = self.config.get("selected_genre", "Cyberpunk")
        selected_row = 0

        for i, genre in enumerate(GENRES):
            item = QListWidgetItem(f"• {genre}")
            item.setData(Qt.ItemDataRole.UserRole, genre)
            self.genre_list.addItem(item)
            if genre.lower() == current_genre.lower():
                selected_row = i

        self.genre_list.setCurrentRow(selected_row)
        self.genre_list.itemClicked.connect(self._on_genre_clicked)
        layout.addWidget(self.genre_list, 1)

        # Divider
        line2 = QFrame(self)
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("color: #334155;")
        layout.addWidget(line2)

        # Quick Navigation
        self.btn_browse = QPushButton("🌐 Browse Online", self)
        self.btn_browse.clicked.connect(lambda: self.nav_changed.emit(0))
        layout.addWidget(self.btn_browse)

        self.btn_favorites = QPushButton("★ Favorites", self)
        self.btn_favorites.clicked.connect(lambda: self.nav_changed.emit(1))
        layout.addWidget(self.btn_favorites)

        self.btn_library = QPushButton("📁 Local Library", self)
        self.btn_library.clicked.connect(lambda: self.nav_changed.emit(2))
        layout.addWidget(self.btn_library)

        self.btn_settings = QPushButton("⚙ Settings", self)
        self.btn_settings.clicked.connect(lambda: self.nav_changed.emit(3))
        layout.addWidget(self.btn_settings)

    def _on_genre_clicked(self, item: QListWidgetItem):
        genre = item.data(Qt.ItemDataRole.UserRole)
        self.config.set("custom_search", "")
        self.search_input.clear()
        self.config.set("selected_genre", genre)
        self.genre_selected.emit(genre)
        self.nav_changed.emit(0)

    def _on_search_submitted(self):
        query = self.search_input.text().strip()
        self.config.set("custom_search", query)
        self.search_submitted.emit(query)
        self.nav_changed.emit(0)
