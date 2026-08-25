"""
Path Utilities for Resource Path Resolution in Python Source and PyInstaller EXE.
"""

import sys
import os


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)
