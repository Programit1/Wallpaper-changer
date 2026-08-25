"""
Static Wallpaper Engine.
Applies static image wallpapers to Windows Desktop using SystemParametersInfoW / IDesktopWallpaper.
Releases memory immediately after applying. Zero idle CPU/GPU consumption.
"""

import os
from utils.win32_utils import set_static_wallpaper


class StaticWallpaperEngine:
    """Manages static desktop wallpaper applying."""

    def __init__(self):
        self.current_wallpaper_path = ""

    def apply_wallpaper(self, image_path: str) -> bool:
        """
        Applies static wallpaper to desktop.
        Releases image object immediately.
        """
        if not os.path.exists(image_path):
            print(f"StaticWallpaperEngine: File does not exist: {image_path}")
            return False

        success = set_static_wallpaper(image_path)
        if success:
            self.current_wallpaper_path = image_path
            print(f"Static wallpaper applied successfully: {os.path.basename(image_path)}")
        else:
            print(f"Failed to apply static wallpaper: {image_path}")

        return success

    def clear(self):
        """Clears reference."""
        self.current_wallpaper_path = ""
