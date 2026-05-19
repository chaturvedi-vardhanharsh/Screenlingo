from __future__ import annotations

from typing import TYPE_CHECKING

import mss
from PIL import Image

if TYPE_CHECKING:
    from .config import AppConfig


def _grab_monitor(sct: mss.MSS, region: tuple[int, int, int, int] | None):
    if region is not None:
        left, top, width, height = region
        monitor = {"left": left, "top": top, "width": width, "height": height}
    else:
        # monitors[0] is all displays combined; [1] is the primary display
        monitors = sct.monitors
        monitor = monitors[1] if len(monitors) > 1 else monitors[0]
    return sct.grab(monitor)


def _screenshot_to_image(shot) -> Image.Image:
    """Convert mss screenshot to PIL Image (compatible with mss 9.x and 10.x)."""
    if hasattr(shot, "rgb"):
        return Image.frombytes("RGB", shot.size, shot.rgb)
    # mss 9.x and older
    return Image.frombytes("RGB", shot.size, shot.bgr, "raw", "BGRX")


def capture_screen(region: tuple[int, int, int, int] | None = None) -> Image.Image:
    """Capture screen or a region (left, top, width, height)."""
    with mss.MSS() as sct:
        shot = _grab_monitor(sct, region)
        return _screenshot_to_image(shot)


def capture_from_config(config: "AppConfig") -> Image.Image:
    return capture_screen(config.capture_region)
