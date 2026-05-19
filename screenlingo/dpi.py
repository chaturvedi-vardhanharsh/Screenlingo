from __future__ import annotations

import sys


def enable_dpi_awareness() -> None:
    """Match Tk/mss coordinates on high-DPI Windows displays."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def get_virtual_screen_bounds() -> tuple[int, int, int, int]:
    """Return (left, top, width, height) spanning all monitors."""
    import mss

    with mss.mss() as sct:
        bounds = sct.monitors[0]
        return (
            int(bounds["left"]),
            int(bounds["top"]),
            int(bounds["width"]),
            int(bounds["height"]),
        )
