"""
Local LRU Cache Manager for Wallpapers and Metadata.
Tracks download dates, last-used timestamps, favorites, and enforces disk space limits.
"""

import os
import json
import time
import shutil
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from utils.image_utils import generate_thumbnail, get_image_info, get_file_hash


class DownloadWorkerSignals(QObject):
    """Signals for background download worker."""
    download_finished = pyqtSignal(str, str, dict)  # (url, local_path, meta)
    download_failed = pyqtSignal(str, str)  # (url, error_message)


class DownloadRunnable(QRunnable):
    """Background runnable worker for non-blocking asynchronous downloads using QThreadPool."""

    def __init__(self, url: str, target_path: str, meta: dict):
        super().__init__()
        self.url = url
        self.target_path = target_path
        self.meta = meta
        self.signals = DownloadWorkerSignals()
        self.setAutoDelete(True)

    def run(self):
        try:
            os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
            resp = requests.get(self.url, stream=True, timeout=20)
            resp.raise_for_status()

            temp_path = self.target_path + ".tmp"
            with open(temp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)

            if os.path.exists(self.target_path):
                os.remove(self.target_path)
            os.rename(temp_path, self.target_path)

            self.signals.download_finished.emit(self.url, self.target_path, self.meta)

        except Exception as e:
            if os.path.exists(self.target_path + ".tmp"):
                try:
                    os.remove(self.target_path + ".tmp")
                except Exception:
                    pass
            self.signals.download_failed.emit(self.url, str(e))


class CacheManager(QObject):
    """Manages local storage, metadata database, LRU eviction, and downloading."""
    download_completed = pyqtSignal(dict)  # wallpaper metadata dict
    download_error = pyqtSignal(str)       # error string

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.cache_dir = self.config.get("cache_dir")
        os.makedirs(self.cache_dir, exist_ok=True)

        self.thumbs_dir = os.path.join(self.cache_dir, "thumbnails")
        os.makedirs(self.thumbs_dir, exist_ok=True)

        self.index_path = os.path.join(self.cache_dir, "cache_index.json")
        self.index: dict[str, dict] = {}
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except Exception as e:
                print(f"Error loading cache index: {e}")
                self.index = {}

    def save_index(self):
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving cache index: {e}")

    def get_wallpaper(self, wp_id: str) -> dict | None:
        return self.index.get(wp_id)

    def is_cached(self, wp_id: str) -> bool:
        item = self.index.get(wp_id)
        if item and os.path.exists(item.get("filepath", "")):
            return True
        return False

    def update_last_used(self, wp_id: str):
        if wp_id in self.index:
            self.index[wp_id]["last_used_timestamp"] = time.time()
            self.save_index()

    def toggle_favorite(self, wp_id: str) -> bool:
        if wp_id in self.index:
            curr = self.index[wp_id].get("favorite", False)
            self.index[wp_id]["favorite"] = not curr
            self.save_index()
            return self.index[wp_id]["favorite"]
        return False

    def add_local_file(self, file_path: str) -> dict | None:
        """Imports a local image file into cache library."""
        if not os.path.exists(file_path):
            return None
        filename = os.path.basename(file_path)
        wp_id = "local_" + get_file_hash(file_path)[:10]

        ext = os.path.splitext(filename)[1].lower()
        target_name = f"{wp_id}{ext}"
        target_path = os.path.join(self.cache_dir, target_name)

        if not os.path.exists(target_path):
            shutil.copy2(file_path, target_path)

        thumb_path = os.path.join(self.thumbs_dir, f"{wp_id}.jpg")
        w, h, fmt = get_image_info(target_path)
        generate_thumbnail(target_path, thumb_path)

        meta = {
            "id": wp_id,
            "filename": target_name,
            "filepath": target_path,
            "thumb_path": thumb_path,
            "source_url": "local",
            "resolution": f"{w}x{h}",
            "file_type": fmt,
            "download_date": time.time(),
            "last_used_timestamp": time.time(),
            "favorite": False,
            "tags": ["local"]
        }

        self.index[wp_id] = meta
        self.save_index()
        self.enforce_cache_limit()
        return meta

    def download_wallpaper(self, item_data: dict):
        """
        Asynchronously downloads a wallpaper from Wallhaven API data object using QThreadPool.
        """
        wp_id = str(item_data.get("id"))
        if self.is_cached(wp_id):
            meta = self.index[wp_id]
            self.update_last_used(wp_id)
            self.download_completed.emit(meta)
            return

        file_url = item_data.get("path")
        if not file_url:
            self.download_error.emit(f"No file URL found for wallpaper {wp_id}")
            return

        ext = os.path.splitext(file_url)[1] or ".jpg"
        target_path = os.path.join(self.cache_dir, f"{wp_id}{ext}")
        thumb_path = os.path.join(self.thumbs_dir, f"{wp_id}.jpg")

        meta = {
            "id": wp_id,
            "filename": f"{wp_id}{ext}",
            "filepath": target_path,
            "thumb_path": thumb_path,
            "source_url": file_url,
            "wallhaven_url": item_data.get("url", ""),
            "resolution": item_data.get("resolution", "1920x1080"),
            "file_type": item_data.get("file_type", ext.replace(".", "").upper()),
            "download_date": time.time(),
            "last_used_timestamp": time.time(),
            "favorite": False,
            "tags": [t.get("name") for t in item_data.get("tags", [])] if isinstance(item_data.get("tags"), list) else []
        }

        runnable = DownloadRunnable(file_url, target_path, meta)
        runnable.signals.download_finished.connect(self._on_download_finished)
        runnable.signals.download_failed.connect(self._on_download_failed)
        QThreadPool.globalInstance().start(runnable)

    def _on_download_finished(self, url: str, local_path: str, meta: dict):
        wp_id = meta["id"]
        thumb_path = meta["thumb_path"]
        generate_thumbnail(local_path, thumb_path)

        self.index[wp_id] = meta
        self.save_index()
        self.enforce_cache_limit()

        self.download_completed.emit(meta)

    def _on_download_failed(self, url: str, error_msg: str):
        self.download_error.emit(f"Download failed: {error_msg}")

    def get_total_cache_size_bytes(self) -> int:
        total = 0
        for wp_id, item in self.index.items():
            path = item.get("filepath")
            if path and os.path.exists(path):
                total += os.path.getsize(path)
        return total

    def enforce_cache_limit(self):
        """
        LRU Eviction algorithm:
        Deletes oldest un-favorited wallpapers when cache size exceeds max_cache_size_mb.
        Never deletes favorited wallpapers.
        """
        max_mb = self.config.get("max_cache_size_mb", 2048)
        if max_mb <= 0:  # 0 means unlimited
            return

        max_bytes = max_mb * 1024 * 1024
        curr_size = self.get_total_cache_size_bytes()

        if curr_size <= max_bytes:
            return

        evictable = [
            item for item in self.index.values()
            if not item.get("favorite", False) and os.path.exists(item.get("filepath", ""))
        ]

        evictable.sort(key=lambda x: x.get("last_used_timestamp", 0))

        for item in evictable:
            if curr_size <= max_bytes:
                break
            filepath = item.get("filepath")
            thumb_path = item.get("thumb_path")
            wp_id = item.get("id")

            if filepath and os.path.exists(filepath):
                try:
                    fsize = os.path.getsize(filepath)
                    os.remove(filepath)
                    curr_size -= fsize
                except Exception as e:
                    print(f"Error removing cached file {filepath}: {e}")

            if thumb_path and os.path.exists(thumb_path):
                try:
                    os.remove(thumb_path)
                except Exception:
                    pass

            if wp_id in self.index:
                del self.index[wp_id]

        self.save_index()

    def clear_cache(self, keep_favorites: bool = True):
        """Clears cached wallpapers."""
        to_delete = []
        for wp_id, item in self.index.items():
            if keep_favorites and item.get("favorite", False):
                continue
            to_delete.append(wp_id)

        for wp_id in to_delete:
            item = self.index[wp_id]
            fpath = item.get("filepath")
            tpath = item.get("thumb_path")
            if fpath and os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass
            if tpath and os.path.exists(tpath):
                try:
                    os.remove(tpath)
                except Exception:
                    pass
            del self.index[wp_id]

        self.save_index()

    def delete_wallpaper(self, wp_id: str):
        """Deletes a specific wallpaper from cache and index."""
        if wp_id in self.index:
            item = self.index[wp_id]
            fpath = item.get("filepath")
            tpath = item.get("thumb_path")
            if fpath and os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass
            if tpath and os.path.exists(tpath):
                try:
                    os.remove(tpath)
                except Exception:
                    pass
            del self.index[wp_id]
            self.save_index()
