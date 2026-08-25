"""
Automated unit verification script for application core modules.
"""

import os
import sys
import time

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from config import ConfigManager
from core.api_client import WallhavenAPIClient
from core.cache_manager import CacheManager
from core.static_engine import StaticWallpaperEngine
from core.scheduler import WallpaperScheduler, INTERVAL_MAP_MS
from utils.win32_utils import is_autostart_enabled
from utils.image_utils import calculate_aspect_ratio, get_file_hash


def test_all():
    print("--- Running Unit & Component Verification ---")

    # 1. Config Manager Test
    cfg = ConfigManager("test_settings.json")
    cfg.set("selected_genre", "Cyberpunk")
    assert cfg.get("selected_genre") == "Cyberpunk", "Config test failed"
    print("[OK] ConfigManager test passed")

    # 2. Wallhaven API Client Test
    api = WallhavenAPIClient(offline_mode=True)
    res = api.search_wallpapers(query="nature")
    assert res.get("meta", {}).get("offline") == True, "API offline test failed"
    print("[OK] WallhavenAPIClient offline test passed")

    # 3. Image Utils Test
    r = calculate_aspect_ratio(1920, 1080)
    assert r == "16x9", f"Aspect ratio calculation failed: {r}"
    h = get_file_hash("test_string")
    assert len(h) == 32, "Hash test failed"
    print("[OK] Image Utils test passed")

    # 4. Cache Manager Test
    cache = CacheManager(cfg)
    test_id = "test_wp_001"
    cache.index[test_id] = {
        "id": test_id,
        "filepath": os.path.abspath(__file__),
        "favorite": True,
        "last_used_timestamp": time.time()
    }
    cache.save_index()

    fav = cache.toggle_favorite(test_id)
    assert fav == False, "Favorite toggle test failed"
    assert cache.is_cached(test_id) == True, "Is cached test failed"
    print("[OK] CacheManager & metadata test passed")

    # 5. Scheduler Interval Test
    assert INTERVAL_MAP_MS["1 Hour"] == 3600000, "Scheduler interval map failed"
    print("[OK] Scheduler interval test passed")

    print("\nALL COMPONENT VERIFICATION TESTS PASSED SUCCESSFULLY!")

    # Cleanup test config file
    if os.path.exists(cfg.config_path):
        try:
            os.remove(cfg.config_path)
        except Exception:
            pass


if __name__ == "__main__":
    test_all()
