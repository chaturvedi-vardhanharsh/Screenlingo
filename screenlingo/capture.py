from __future__ import annotations

from typing import TYPE_CHECKING

import mss
from PIL import Image

if TYPE_CHECKING:
    from .config import AppConfig


def capture_screen(region: tuple[int, int, int, int] | None = None) -> Image.Image:
    """Capture screen or a region (left, top, width, height)."""
    with mss.mss() as sct:
        if region is None:
            monitor = sct.monitors[0]
        else:
            left, top, width, height = region
            monitor = {"left": left, "top": top, "width": width, "height": height}
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.bgr, "raw", "BGRX")


def capture_from_config(config: "AppConfig") -> Image.Image:
    return capture_screen(config.capture_region)
