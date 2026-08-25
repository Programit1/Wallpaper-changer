"""
Image helper utilities: thumbnail generation, aspect ratio calculation, file hashing.
"""

import os
import hashlib
from PIL import Image


def get_file_hash(filepath: str) -> str:
    """Generates MD5 hash for a given file or URL string."""
    return hashlib.md5(filepath.encode("utf-8")).hexdigest()


def generate_thumbnail(image_path: str, thumb_path: str, max_size=(320, 180)) -> bool:
    """
    Generates a low-memory thumbnail preview for the library view.
    Does not keep full-resolution image loaded in RAM.
    """
    if os.path.exists(thumb_path):
        return True
    try:
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.convert("RGB").save(thumb_path, "JPEG", quality=85)
        return True
    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")
        return False


def get_image_info(filepath: str) -> tuple[int, int, str]:
    """
    Extracts image width, height, and format without decoding full pixel data.
    """
    try:
        with Image.open(filepath) as img:
            return img.width, img.height, img.format or "JPEG"
    except Exception:
        return 0, 0, "UNKNOWN"


def calculate_aspect_ratio(width: int, height: int) -> str:
    """Calculates aspect ratio string like 16x9, 16x10, 21x9."""
    if not width or not height:
        return "16x9"
    ratio = width / height
    if abs(ratio - (16 / 9)) < 0.05:
        return "16x9"
    elif abs(ratio - (16 / 10)) < 0.05:
        return "16x10"
    elif abs(ratio - (21 / 9)) < 0.05:
        return "21x9"
    elif abs(ratio - (32 / 9)) < 0.05:
        return "32x9"
    elif abs(ratio - (4 / 3)) < 0.05:
        return "4x3"
    elif abs(ratio - 1.0) < 0.05:
        return "1x1"
    elif abs(ratio - (9 / 16)) < 0.05:
        return "9x16"
    return f"{width}x{height}"
