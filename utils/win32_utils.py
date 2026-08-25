"""
Win32 Low-Level Utilities for Static Wallpaper Setting and Windows Registry Autostart.
"""

import os
import sys
import ctypes
from ctypes import wintypes
import winreg

user32 = ctypes.windll.user32

user32.SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT, wintypes.LPCWSTR, wintypes.UINT]
user32.SystemParametersInfoW.restype = wintypes.BOOL

SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

REG_APP_NAME = "WallhavenWallpaperChanger"


def set_static_wallpaper(image_path: str) -> bool:
    """
    Sets the Windows desktop wallpaper using SystemParametersInfoW.
    Releases image memory immediately.
    """
    if not os.path.exists(image_path):
        return False
    abs_path = os.path.abspath(image_path)
    res = user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        abs_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return bool(res)


def set_autostart(enabled: bool) -> bool:
    """Configures application auto-start with Windows login via HKCU Run registry key."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        if enabled:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}" --minimized'
            winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, REG_APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Registry error setting autostart: {e}")
        return False


def is_autostart_enabled() -> bool:
    """Checks if autostart registry key is currently present."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False
