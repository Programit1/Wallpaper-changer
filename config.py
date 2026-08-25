"""
Configuration Manager handling persistence (settings.json) and defaults.
"""

import os
import json
from utils.win32_utils import set_autostart, is_autostart_enabled

GENRES = [
    "Cyberpunk", "Anime", "Nature", "Mountains", "Space",
    "Cars", "Gaming", "Minimal", "Architecture", "City",
    "Abstract", "Dark", "Random"
]

RESOLUTION_PRESETS = {
    "Any": "",
    "1080p": "1920x1080",
    "1440p": "2560x1440",
    "4K": "3840x2160",
    "Ultrawide": "2560x1080,3440x1440"
}

DEFAULT_CONFIG = {
    # General Settings
    "start_with_windows": False,
    "start_minimized": False,
    
    # Wallpaper & Genre Settings
    "rotation_interval": "1 Hour",  # Manual, 30 Mins, 1 Hour, 3 Hours, 6 Hours, Daily
    "selected_genre": "Cyberpunk",
    "custom_search": "",
    "categories": {"general": True, "anime": True, "people": False},
    "purity": {"sfw": True, "sketchy": False, "nsfw": False},
    "sorting": "random",  # random, relevance, date_added, views, favorites, toplist
    "resolution_preset": "1080p",  # Any, 1080p, 1440p, 4K, Ultrawide
    "resolution_preference": "1920x1080",
    "aspect_ratios": ["16x9"],
    
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

    def get_active_query(self) -> str:
        """Returns the active search query (custom search if provided, else selected genre)."""
        custom = self.data.get("custom_search", "").strip()
        if custom:
            return custom
        genre = self.data.get("selected_genre", "Random")
        if genre.lower() == "random":
            return ""
        return genre

    def get_resolution_param(self) -> str:
        """Returns API resolution parameter corresponding to resolution preset."""
        preset = self.data.get("resolution_preset", "Any")
        return RESOLUTION_PRESETS.get(preset, "")

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
