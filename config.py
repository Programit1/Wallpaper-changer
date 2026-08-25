"""
Configuration Manager handling persistence (settings.json) and defaults.
"""

import os
import json
from utils.win32_utils import set_autostart, is_autostart_enabled

DEFAULT_CONFIG = {
    # General Settings
    "start_with_windows": False,
    "start_minimized": False,
    
    # Wallpaper Settings
    "rotation_interval": "1 Hour",  # 5 Mins, 15 Mins, 30 Mins, 1 Hour, 3 Hours, 6 Hours, Daily, Manual
    "search_query": "nature",
    "categories": {"general": True, "anime": True, "people": False},  # 110
    "purity": {"sfw": True, "sketchy": False, "nsfw": False},       # 100
    "sorting": "random",  # random, relevance, date_added, views, favorites, toplist
    "resolution_preference": "1920x1080",
    "aspect_ratios": ["16x9"],
    "tags": [],
    
    # Storage & Cache Settings
    "cache_dir": os.path.join(os.path.expanduser("~"), ".wallhaven_cache"),
    "max_cache_size_mb": 2048,  # 500, 1024, 2048, 5120, 10240, 0 (Unlimited)
    
    # Network Settings
    "api_key": "",  # Wallhaven API Key (optional)
    "download_concurrency": 2,
    "offline_mode": False
}


class ConfigManager:
    """Manages application settings loading and saving."""

    def __init__(self, config_filename="settings.json"):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".wallhaven_wallpaper_changer")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, config_filename)
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"Failed to load settings from {self.config_path}: {e}")

        # Ensure cache dir exists
        os.makedirs(self.data["cache_dir"], exist_ok=True)

        # Synchronize registry autostart state if needed
        registry_enabled = is_autostart_enabled()
        if self.data["start_with_windows"] != registry_enabled:
            set_autostart(self.data["start_with_windows"])

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings to {self.config_path}: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        if key == "start_with_windows":
            set_autostart(value)
        self.save()

    def get_categories_string(self) -> str:
        """Returns 3-digit category code string (e.g. '110')."""
        cats = self.data.get("categories", {})
        g = "1" if cats.get("general", True) else "0"
        a = "1" if cats.get("anime", True) else "0"
        p = "1" if cats.get("people", False) else "0"
        return f"{g}{a}{p}"

    def get_purity_string(self) -> str:
        """Returns 3-digit purity code string (e.g. '100')."""
        pur = self.data.get("purity", {})
        sfw = "1" if pur.get("sfw", True) else "0"
        ske = "1" if pur.get("sketchy", False) else "0"
        nsfw = "1" if pur.get("nsfw", False) else "0"
        return f"{sfw}{ske}{nsfw}"
