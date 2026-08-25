"""
Core Wallpaper Manager.
Coordinates Wallhaven API, local cache, static engine, monitors, and scheduler.
"""

import os
import random
from PyQt6.QtCore import QObject, pyqtSignal
from core.api_client import WallhavenAPIClient
from core.cache_manager import CacheManager
from core.static_engine import StaticWallpaperEngine
from core.monitor_manager import MonitorManager
from core.scheduler import WallpaperScheduler


class WallpaperManager(QObject):
    """Central orchestrator for desktop wallpapers."""

    wallpaper_changed = pyqtSignal(dict)       # Emits current wallpaper metadata dict
    status_message = pyqtSignal(str)          # Emits human readable status string

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.api_client = WallhavenAPIClient(
            api_key=self.config.get("api_key", ""),
            offline_mode=self.config.get("offline_mode", False)
        )
        self.cache_manager = CacheManager(self.config)
        self.static_engine = StaticWallpaperEngine()
        self.scheduler = WallpaperScheduler(self.config)

        self.current_wallpaper: dict | None = None
        self.history: list[dict] = []
        self.history_index: int = -1

        # Connect Signals
        self.cache_manager.download_completed.connect(self._on_download_completed)
        self.cache_manager.download_error.connect(self._on_download_error)
        self.scheduler.rotation_triggered.connect(self.fetch_next_wallpaper)

    def fetch_next_wallpaper(self):
        """Fetches and sets next wallpaper (online from Wallhaven or offline from cache)."""
        self.status_message.emit("Fetching wallpaper...")

        if self.config.get("offline_mode", False):
            self._apply_random_offline_wallpaper()
            return

        # Fetch from Wallhaven API
        query = self.config.get("search_query", "")
        cats = self.config.get_categories_string()
        purity = self.config.get_purity_string()
        sorting = self.config.get("sorting", "random")
        res = self.config.get("resolution_preference", "")
        ratios = ",".join(self.config.get("aspect_ratios", ["16x9"]))

        res_data = self.api_client.search_wallpapers(
            query=query,
            categories=cats,
            purity=purity,
            sorting=sorting,
            resolutions=res,
            ratios=ratios
        )

        data_list = res_data.get("data", [])
        if not data_list:
            print("Wallhaven search returned no items or network offline; falling back to local cache.")
            self._apply_random_offline_wallpaper()
            return

        item = random.choice(data_list)
        self.cache_manager.download_wallpaper(item)

    def _on_download_completed(self, meta: dict):
        self.apply_wallpaper_item(meta)

    def _on_download_error(self, error_msg: str):
        self.status_message.emit(error_msg)
        print(f"WallpaperManager error: {error_msg}. Falling back to cached wallpaper.")
        self._apply_random_offline_wallpaper()

    def apply_wallpaper_item(self, meta: dict):
        """Applies a wallpaper metadata dict to desktop."""
        filepath = meta.get("filepath")
        if not filepath or not os.path.exists(filepath):
            self.status_message.emit("Error: Wallpaper file not found")
            return

        wp_id = meta.get("id")
        self.cache_manager.update_last_used(wp_id)
        self.current_wallpaper = meta

        # Manage history
        if not self.history or self.history[-1].get("id") != wp_id:
            self.history.append(meta)
            self.history_index = len(self.history) - 1

        self.static_engine.apply_wallpaper(filepath)

        self.wallpaper_changed.emit(meta)
        self.status_message.emit(f"Wallpaper updated: {meta.get('resolution', 'Unknown')}")

    def fetch_previous_wallpaper(self):
        """Navigates back in history stack."""
        if self.history_index > 0:
            self.history_index -= 1
            prev_meta = self.history[self.history_index]
            self.apply_wallpaper_item(prev_meta)

    def fetch_next_in_history(self):
        """Navigates forward in history or fetches new."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            next_meta = self.history[self.history_index]
            self.apply_wallpaper_item(next_meta)
        else:
            self.fetch_next_wallpaper()

    def _apply_random_offline_wallpaper(self):
        """Picks a random previously cached wallpaper."""
        cached_items = list(self.cache_manager.index.values())
        valid_items = [
            item for item in cached_items
            if os.path.exists(item.get("filepath", ""))
        ]
        if not valid_items:
            self.status_message.emit("Offline mode: No cached wallpapers found in library")
            return

        meta = random.choice(valid_items)
        self.apply_wallpaper_item(meta)

    def toggle_current_favorite(self) -> bool:
        if self.current_wallpaper:
            wp_id = self.current_wallpaper.get("id")
            fav = self.cache_manager.toggle_favorite(wp_id)
            self.current_wallpaper["favorite"] = fav
            self.wallpaper_changed.emit(self.current_wallpaper)
            return fav
        return False

    def shutdown(self):
        """Clean application shutdown handler."""
        print("WallpaperManager shutting down...")
        self.scheduler.timer.stop()
