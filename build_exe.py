"""
PyInstaller Packaging Build Script.
Compiles main.py into dist/GitHubWallpaperChanger.exe
"""

import os
import sys
import subprocess


def build():
    print("=== Building Standalone Windows Executable with PyInstaller ===")

    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_dir, "main.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",  # create a single directory bundle (or --onefile for single EXE)
        "--windowed", # no console window
        "--name", "GitHubWallpaperChanger",
        "--paths", project_dir,
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "win32gui",
        "--hidden-import", "win32con",
        main_script
    ]

    print("Running command:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=project_dir)

    if res.returncode == 0:
        exe_path = os.path.join(project_dir, "dist", "GitHubWallpaperChanger", "GitHubWallpaperChanger.exe")
        print("\n✔ PyInstaller Build Completed Successfully!")
        print(f"Executable Location: {exe_path}")
    else:
        print(f"\n✖ Build Failed with return code {res.returncode}")


if __name__ == "__main__":
    build()
