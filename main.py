"""
Application Entry Point for Wallhaven Wallpaper Changer.
Handles single-instance application enforcement, system tray, and GUI loop.
"""

import sys
import os

# Ensure project root directory is in python sys.path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSystemSemaphore, QSharedMemory, Qt
from config import ConfigManager
from core.wallpaper_manager import WallpaperManager
from ui.styles import DARK_STYLESHEET
from ui.system_tray import SystemTrayIcon
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray when main window is closed
    app.setStyleSheet(DARK_STYLESHEET)

    # Single-instance enforcement
    semaphore = QSystemSemaphore("WallhavenWallpaperChanger_Sem", 1)
    semaphore.acquire()

    shared_mem = QSharedMemory("WallhavenWallpaperChanger_Mem")
    is_running = not shared_mem.create(1)
    semaphore.release()

    if is_running:
        print("Wallhaven Wallpaper Changer is already running in background.")
        sys.exit(0)

    # Initialize Core Managers
    config_mgr = ConfigManager()
    wp_mgr = WallpaperManager(config_mgr)

    # Initialize System Tray and Main UI
    tray_icon = SystemTrayIcon(wp_mgr)
    main_window = MainWindow(wp_mgr, config_mgr)
    main_window.set_tray_ref(tray_icon)

    # Connect Tray Signals to Main Window
    tray_icon.open_main_requested.connect(main_window.showNormal)
    tray_icon.open_main_requested.connect(main_window.activateWindow)
    tray_icon.open_library_requested.connect(lambda: (main_window.tab_widget.setCurrentIndex(1), main_window.showNormal(), main_window.activateWindow()))
    tray_icon.open_settings_requested.connect(main_window.open_settings)
    
    def on_exit():
        wp_mgr.shutdown()
        app.quit()

    tray_icon.exit_requested.connect(on_exit)

    # Handle CLI --minimized flag or config setting
    start_minimized = "--minimized" in sys.argv or config_mgr.get("start_minimized", False)
    if not start_minimized:
        main_window.show()

    # Apply initial wallpaper or load last used
    cached_wallpapers = list(wp_mgr.cache_manager.index.values())
    if cached_wallpapers:
        # Load last used wallpaper on startup
        cached_wallpapers.sort(key=lambda x: x.get("last_used_timestamp", 0), reverse=True)
        wp_mgr.apply_wallpaper_item(cached_wallpapers[0])
    else:
        # Fetch initial wallpaper from Wallhaven
        wp_mgr.fetch_next_wallpaper()

    ret = app.exec()

    # Ensure clean shutdown and memory cleanup
    wp_mgr.shutdown()
    sys.exit(ret)


if __name__ == "__main__":
    main()
