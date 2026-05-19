from __future__ import annotations

import sys
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGOS_DIR = ASSETS_DIR / "logos"
DEFAULT_ICO = ASSETS_DIR / "app_icon.ico"

LOGO_CHOICES = {
    "A — Globe": LOGOS_DIR / "logo_a_globe.png",
    "B — Speech": LOGOS_DIR / "logo_b_speech.png",
    "C — Monogram": LOGOS_DIR / "logo_c_monogram.png",
    "D — Screen": LOGOS_DIR / "logo_d_screen.png",
}


def apply_window_icon(window) -> None:
    """Set window + Windows taskbar icon (replaces default Python icon)."""
    if not DEFAULT_ICO.exists():
        return
    path = str(DEFAULT_ICO.resolve())
    try:
        if sys.platform == "win32":
            window.iconbitmap(default=path)
            try:
                window.wm_iconbitmap(bitmap=path)
            except Exception:
                pass
            # Distinct taskbar grouping on Windows
            try:
                import ctypes

                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "ScreenLingo.ScreenTranslator.1"
                )
            except Exception:
                pass
        else:
            window.iconphoto(True, _tk_photo(window, path))
    except Exception:
        pass


def _tk_photo(window, ico_path: str):
    from tkinter import PhotoImage

    # Fallback: use PNG if ICO fails on non-Windows
    png = LOGOS_DIR / "logo_a_globe.png"
    if png.exists():
        return PhotoImage(file=str(png), master=window)
    return PhotoImage(file=ico_path, master=window)


def set_app_icon_from_choice(choice_key: str) -> bool:
    """Build app_icon.ico from a logo PNG choice. Returns success."""
    png = LOGO_CHOICES.get(choice_key)
    if png is None or not png.exists():
        return False
    try:
        from PIL import Image

        img = Image.open(png).convert("RGBA")
        sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(DEFAULT_ICO, format="ICO", sizes=sizes)
        return True
    except Exception:
        return False
