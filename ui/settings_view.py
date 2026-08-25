"""
Settings View Dialog.
Tabbed interface for General, Wallhaven API, Storage, and Network options.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QCheckBox, QLabel, QComboBox, QLineEdit, QPushButton, QGroupBox,
    QMessageBox
)
from config import RESOLUTION_PRESETS


class SettingsDialog(QDialog):
    """Full Settings Dialog."""

    def __init__(self, config_manager, wallpaper_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.wm = wallpaper_manager
        self.setWindowTitle("Settings - Wallhaven Wallpaper Changer")
        self.setMinimumSize(540, 420)

        self._init_ui()
        self.load_values()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        # Tab 1: General Options
        gen_tab = QWidget()
        gen_layout = QVBoxLayout(gen_tab)
        
        self.chk_start_windows = QCheckBox("Start with Windows login", self)
        gen_layout.addWidget(self.chk_start_windows)

        self.chk_start_minimized = QCheckBox("Start minimized to System Tray", self)
        gen_layout.addWidget(self.chk_start_minimized)

        gen_layout.addStretch()
        self.tabs.addTab(gen_tab, "General")

        # Tab 2: Wallhaven API & Resolution Settings
        wp_tab = QWidget()
        wp_layout = QVBoxLayout(wp_tab)

        int_box = QHBoxLayout()
        int_box.addWidget(QLabel("Auto Rotation Interval:", self))
        self.combo_interval = QComboBox(self)
        self.combo_interval.addItems(["Manual", "30 Mins", "1 Hour", "3 Hours", "6 Hours", "Daily"])
        int_box.addWidget(self.combo_interval)
        int_box.addStretch()
        wp_layout.addLayout(int_box)

        res_box = QHBoxLayout()
        res_box.addWidget(QLabel("Resolution Filter:", self))
        self.combo_resolution = QComboBox(self)
        self.combo_resolution.addItems(list(RESOLUTION_PRESETS.keys()))
        res_box.addWidget(self.combo_resolution)
        res_box.addStretch()
        wp_layout.addLayout(res_box)

        cat_group = QGroupBox("Categories", self)
        cat_l = QHBoxLayout(cat_group)
        self.chk_cat_general = QCheckBox("General", self)
        self.chk_cat_anime = QCheckBox("Anime", self)
        self.chk_cat_people = QCheckBox("People", self)
        cat_l.addWidget(self.chk_cat_general)
        cat_l.addWidget(self.chk_cat_anime)
        cat_l.addWidget(self.chk_cat_people)
        wp_layout.addWidget(cat_group)

        pur_group = QGroupBox("Purity Filter", self)
        pur_l = QHBoxLayout(pur_group)
        self.chk_pur_sfw = QCheckBox("SFW", self)
        self.chk_pur_sketchy = QCheckBox("Sketchy", self)
        self.chk_pur_nsfw = QCheckBox("NSFW (Requires API Key)", self)
        pur_l.addWidget(self.chk_pur_sfw)
        pur_l.addWidget(self.chk_pur_sketchy)
        pur_l.addWidget(self.chk_pur_nsfw)
        wp_layout.addWidget(pur_group)

        sort_box = QHBoxLayout()
        sort_box.addWidget(QLabel("Sorting Strategy:", self))
        self.combo_sorting = QComboBox(self)
        self.combo_sorting.addItems(["random", "relevance", "date_added", "views", "favorites", "toplist"])
        sort_box.addWidget(self.combo_sorting)
        sort_box.addStretch()
        wp_layout.addLayout(sort_box)

        wp_layout.addStretch()
        self.tabs.addTab(wp_tab, "Wallhaven")

        # Tab 3: Storage & Cache
        store_tab = QWidget()
        store_layout = QVBoxLayout(store_tab)

        cache_limit_box = QHBoxLayout()
        cache_limit_box.addWidget(QLabel("Maximum Cache Size:", self))
        self.combo_cache_size = QComboBox(self)
        self.combo_cache_size.addItems(["500 MB", "1 GB", "2 GB", "5 GB", "10 GB", "Unlimited"])
        cache_limit_box.addWidget(self.combo_cache_size)
        cache_limit_box.addStretch()
        store_layout.addLayout(cache_limit_box)

        btn_box = QHBoxLayout()
        self.btn_clear_cache = QPushButton("Clear Cache (Keep Favorites)", self)
        self.btn_clear_cache.clicked.connect(self._clear_cache)
        btn_box.addWidget(self.btn_clear_cache)

        self.btn_clear_all = QPushButton("Clear All Cache", self)
        self.btn_clear_all.setObjectName("DangerButton")
        self.btn_clear_all.clicked.connect(self._clear_all_cache)
        btn_box.addWidget(self.btn_clear_all)
        store_layout.addLayout(btn_box)

        store_layout.addStretch()
        self.tabs.addTab(store_tab, "Storage")

        # Tab 4: Network Options
        net_tab = QWidget()
        net_layout = QVBoxLayout(net_tab)

        api_box = QHBoxLayout()
        api_box.addWidget(QLabel("Wallhaven API Key:", self))
        self.txt_api_key = QLineEdit(self)
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("Optional API key for SFW/NSFW search")
        api_box.addWidget(self.txt_api_key)
        net_layout.addLayout(api_box)

        self.chk_offline = QCheckBox("Offline Mode (Use cached wallpapers only)", self)
        net_layout.addWidget(self.chk_offline)

        net_layout.addStretch()
        self.tabs.addTab(net_tab, "Network")

        # Bottom Action Buttons
        bottom_btns = QHBoxLayout()
        bottom_btns.addStretch()

        self.btn_save = QPushButton("Save Settings", self)
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.save_values)
        bottom_btns.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        bottom_btns.addWidget(self.btn_cancel)

        main_layout.addLayout(bottom_btns)

    def load_values(self):
        self.chk_start_windows.setChecked(self.config.get("start_with_windows", False))
        self.chk_start_minimized.setChecked(self.config.get("start_minimized", False))

        self.combo_interval.setCurrentText(self.config.get("rotation_interval", "1 Hour"))
        self.combo_resolution.setCurrentText(self.config.get("resolution_preset", "Any"))

        cats = self.config.get("categories", {})
        self.chk_cat_general.setChecked(cats.get("general", True))
        self.chk_cat_anime.setChecked(cats.get("anime", True))
        self.chk_cat_people.setChecked(cats.get("people", False))

        pur = self.config.get("purity", {})
        self.chk_pur_sfw.setChecked(pur.get("sfw", True))
        self.chk_pur_sketchy.setChecked(pur.get("sketchy", False))
        self.chk_pur_nsfw.setChecked(pur.get("nsfw", False))

        self.combo_sorting.setCurrentText(self.config.get("sorting", "random"))

        max_mb = self.config.get("max_cache_size_mb", 2048)
        mb_map = {500: "500 MB", 1024: "1 GB", 2048: "2 GB", 5120: "5 GB", 10240: "10 GB", 0: "Unlimited"}
        self.combo_cache_size.setCurrentText(mb_map.get(max_mb, "2 GB"))

        self.txt_api_key.setText(self.config.get("api_key", ""))
        self.chk_offline.setChecked(self.config.get("offline_mode", False))

    def save_values(self):
        self.config.set("start_with_windows", self.chk_start_windows.isChecked())
        self.config.set("start_minimized", self.chk_start_minimized.isChecked())

        old_interval = self.config.get("rotation_interval")
        new_interval = self.combo_interval.currentText()
        self.config.set("rotation_interval", new_interval)
        if old_interval != new_interval:
            self.wm.scheduler.update_interval()

        self.config.set("resolution_preset", self.combo_resolution.currentText())

        self.config.set("categories", {
            "general": self.chk_cat_general.isChecked(),
            "anime": self.chk_cat_anime.isChecked(),
            "people": self.chk_cat_people.isChecked()
        })

        self.config.set("purity", {
            "sfw": self.chk_pur_sfw.isChecked(),
            "sketchy": self.chk_pur_sketchy.isChecked(),
            "nsfw": self.chk_pur_nsfw.isChecked()
        })

        self.config.set("sorting", self.combo_sorting.currentText())

        size_str = self.combo_cache_size.currentText()
        str_map = {"500 MB": 500, "1 GB": 1024, "2 GB": 2048, "5 GB": 5120, "10 GB": 10240, "Unlimited": 0}
        self.config.set("max_cache_size_mb", str_map.get(size_str, 2048))

        api_key = self.txt_api_key.text().strip()
        self.config.set("api_key", api_key)
        self.wm.api_client.set_api_key(api_key)

        offline = self.chk_offline.isChecked()
        self.config.set("offline_mode", offline)
        self.wm.api_client.set_offline_mode(offline)

        self.accept()

    def _clear_cache(self):
        self.wm.cache_manager.clear_cache(keep_favorites=True)
        QMessageBox.information(self, "Cache Cleared", "Local cache cleared (Favorites preserved).")

    def _clear_all_cache(self):
        confirm = QMessageBox.question(
            self, "Clear All Cache", "Are you sure you want to delete ALL cached wallpapers including favorites?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.wm.cache_manager.clear_cache(keep_favorites=False)
            QMessageBox.information(self, "Cache Cleared", "All cached wallpapers deleted.")
