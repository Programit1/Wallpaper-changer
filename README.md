# Wallhaven Desktop Wallpaper Changer (Genre Selection + Online Grid + EXE)

A lightweight, modern Windows desktop utility built with **Python 3.12** and **PyQt6** that uses the **Wallhaven API** to browse, search, and automatically rotate high-resolution static desktop wallpapers.

---

## Upgrade Features

* **Genre & Category Selection**:
  * Quick-select categories from the left sidebar: **Anime, Nature, Mountains, Space, Cars, Gaming, Cyberpunk, Minimal, Architecture, City, Abstract, Dark, Random**.
  * Custom free-text search (e.g. `dark cyberpunk city`).
* **Online Thumbnail Grid Browser**:
  * Clean interactive grid showing search results fetched directly from Wallhaven API.
  * Asynchronously loads thumbnail previews for smooth browsing.
  * Each wallpaper item includes **[Set as Wallpaper]**, **[Favorite (★)]**, and **[Download / Save]** buttons.
* **Resolution & Aspect Ratio Filtering**:
  * Filter search results by resolution presets: **Any, 1080p (1920x1080), 1440p (2560x1440), 4K (3840x2160), Ultrawide (2560x1080, 3440x1440)**.
* **Favorites Section**:
  * Dedicated Favorites section preserving liked wallpapers across application restarts.
* **Automatic Rotation Scheduler**:
  * Rotates desktop wallpapers automatically based on the selected Genre/Category or Custom Search term.
  * Interval presets: **Manual, 30 Mins, 1 Hour, 3 Hours, 6 Hours, Daily**.
* **Standalone Windows Executable**:
  * Compiled with PyInstaller into `dist/GitHubWallpaperChanger/GitHubWallpaperChanger.exe`.
  * Runs on Windows without requiring Python or dependencies to be installed.

---

## Project Structure

```text
wallhaven_wallpaper_changer/
├── main.py                    # Entry point, single-instance lock, system tray
├── config.py                  # Settings manager (settings.json persistence)
├── requirements.txt           # Python dependency specifications
├── build_exe.py               # PyInstaller executable build script
├── GitHubWallpaperChanger.spec# PyInstaller bundle specification
├── core/
│   ├── api_client.py          # Wallhaven REST API client
│   ├── cache_manager.py       # Local LRU cache system & download worker thread
│   ├── wallpaper_manager.py   # Main wallpaper manager & scheduler coordinator
│   ├── static_engine.py       # Win32 SystemParametersInfo wallpaper applier
│   ├── monitor_manager.py     # Multi-monitor enumeration and geometry detection
│   └── scheduler.py           # Event-driven wallpaper rotation timer
├── ui/
│   ├── main_window.py         # Main dashboard UI integrating sidebar & grid browser
│   ├── sidebar.py             # Left navigation sidebar with genre selector & search bar
│   ├── online_grid_view.py    # Online wallpaper search thumbnail grid view
│   ├── library_view.py        # Local library & favorites grid view
│   ├── settings_view.py       # Tabbed settings dialog (General, Wallhaven, Storage, Network)
│   ├── system_tray.py         # System tray icon and context menu
│   └── styles.py              # Modern dark theme stylesheet
└── utils/
    ├── win32_utils.py         # Win32 SystemParametersInfo & autostart registry helpers
    ├── path_utils.py          # Dynamic PyInstaller / dev resource path resolver
    └── image_utils.py         # Thumbnail generator & image metadata helper
```

---

## Quick Start

### 1. Run from Source
```powershell
pip install -r requirements.txt
python main.py
```

### 2. Build Windows Executable
To package the project into a standalone executable:
```powershell
python build_exe.py
```
The output executable will be created at:
`dist/GitHubWallpaperChanger/GitHubWallpaperChanger.exe`

---

## API Configuration & Features

* **Wallhaven API**: Searches `https://wallhaven.cc/api/v1/search` with server-side query parameters (`q`, `categories`, `purity`, `sorting`, `resolutions`).
* **API Key**: Enter your optional Wallhaven API Key in **Settings -> Network** to unlock SFW/NSFW search capability.
* **Offline Fallback**: When offline or if API requests fail, the application falls back to your previously downloaded local cache library.