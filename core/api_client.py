"""
Wallhaven API v1 Client.
Handles searching, rate limits (HTTP 429), timeouts, errors, and offline fallback.
"""

import time
import requests
from typing import List, Dict, Any, Optional

WALLHAVEN_API_BASE = "https://wallhaven.cc/api/v1"


class WallhavenAPIClient:
    """Robust client for Wallhaven REST API."""

    def __init__(self, api_key: str = "", offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WallhavenDesktopChanger/1.0 (Windows Utility)"
        })
        self.last_request_time = 0.0
        self.min_request_interval = 0.5  # 500ms between requests to avoid rate limits

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def set_offline_mode(self, offline: bool):
        self.offline_mode = offline

    def search_wallpapers(
        self,
        query: str = "",
        categories: str = "110",
        purity: str = "100",
        sorting: str = "random",
        order: str = "desc",
        resolutions: str = "",
        ratios: str = "",
        page: int = 1,
        seed: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes search request against Wallhaven API.
        Returns dictionary with 'data' list and 'meta' pagination info.
        """
        if self.offline_mode:
            return {"data": [], "meta": {"offline": True, "error": "Offline mode enabled"}}

        # Rate limiting delay check
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        params = {
            "categories": categories,
            "purity": purity,
            "sorting": sorting,
            "order": order,
            "page": page
        }

        if query.strip():
            params["q"] = query.strip()
        if self.api_key.strip():
            params["apikey"] = self.api_key.strip()
        if resolutions.strip():
            params["resolutions"] = resolutions.strip()
        if ratios.strip():
            params["ratios"] = ratios.strip()
        if seed:
            params["seed"] = seed

        url = f"{WALLHAVEN_API_BASE}/search"

        try:
            self.last_request_time = time.time()
            resp = self.session.get(url, params=params, timeout=10)

            if resp.status_code == 429:
                # Rate limit encountered - sleep 2 seconds and report error
                time.sleep(2.0)
                return {"data": [], "meta": {"error": "Rate limit exceeded (HTTP 429)"}}

            resp.raise_for_status()
            data = resp.json()
            return data

        except requests.exceptions.Timeout:
            print("Wallhaven API Request Timed Out")
            return {"data": [], "meta": {"error": "Request timed out"}}
        except requests.exceptions.RequestException as e:
            print(f"Wallhaven API Network Error: {e}")
            return {"data": [], "meta": {"error": str(e)}}
        except ValueError:
            print("Wallhaven API returned invalid JSON response")
            return {"data": [], "meta": {"error": "Invalid JSON response"}}

    def get_wallpaper_details(self, wallpaper_id: str) -> Optional[Dict[str, Any]]:
        """Fetches detailed metadata for a specific wallpaper ID."""
        if self.offline_mode:
            return None

        url = f"{WALLHAVEN_API_BASE}/w/{wallpaper_id}"
        params = {}
        if self.api_key.strip():
            params["apikey"] = self.api_key.strip()

        try:
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("data")
        except Exception as e:
            print(f"Error fetching details for wallpaper {wallpaper_id}: {e}")
        return None
