#!/usr/bin/env python3
"""Generate ScreenLingo logo options and Windows .ico for taskbar."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "logos"
OUT_ICO = ROOT / "assets" / "app_icon.ico"

BG = "#1a1a2e"
ACCENT = "#3b8ed0"
ACCENT2 = "#7fdbca"
WHITE = "#f0f4f8"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _new() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def logo_a_globe() -> Image.Image:
    img, d = _new()
    d.ellipse((28, 28, 228, 228), fill=BG, outline=ACCENT, width=6)
    d.ellipse((48, 48, 208, 208), outline=ACCENT2, width=3)
    d.arc((48, 48, 208, 208), 0, 360, fill=ACCENT2, width=2)
    d.line((128, 52, 128, 204), fill=ACCENT2, width=2)
    d.arc((68, 48, 188, 208), 0, 360, fill=ACCENT2, width=2)
    d.text((88, 96), "SL", fill=WHITE, font=_font(56))
    return img


def logo_b_speech() -> Image.Image:
    img, d = _new()
    d.rounded_rectangle((40, 36, 216, 176), radius=28, fill=BG, outline=ACCENT, width=6)
    d.polygon([(88, 176), (108, 210), (128, 176)], fill=BG, outline=ACCENT)
    d.line((72, 88, 184, 88), fill=ACCENT2, width=4)
    d.line((72, 108, 160, 108), fill=WHITE, width=4)
    d.line((184, 108, 210, 88), fill=ACCENT2, width=4)
    d.polygon([(210, 82), (230, 72), (210, 98)], fill=ACCENT2)
    return img


def logo_c_monogram() -> Image.Image:
    img, d = _new()
    d.rounded_rectangle((36, 36, 220, 220), radius=40, fill=BG, outline=ACCENT, width=8)
    d.text((72, 78), "SL", fill=WHITE, font=_font(64))
    d.rounded_rectangle((36, 200, 220, 220), fill=ACCENT2)
    return img


def logo_d_screen() -> Image.Image:
    img, d = _new()
    d.rounded_rectangle((44, 40, 212, 184), radius=12, fill=BG, outline=ACCENT, width=6)
    d.rectangle((60, 56, 196, 168), fill="#0f0f1a")
    for y in (72, 96, 120, 144):
        d.line((72, y, 184, y), fill=ACCENT2, width=3)
    d.rounded_rectangle((96, 188, 160, 210), radius=6, fill=ACCENT)
    d.text((100, 100), "Aa", fill=WHITE, font=_font(40))
    return img


def save_all() -> None:
    LOGOS.mkdir(parents=True, exist_ok=True)
    variants = {
        "logo_a_globe.png": logo_a_globe(),
        "logo_b_speech.png": logo_b_speech(),
        "logo_c_monogram.png": logo_c_monogram(),
        "logo_d_screen.png": logo_d_screen(),
    }
    for name, im in variants.items():
        im.save(LOGOS / name, format="PNG")
    default = variants["logo_a_globe.png"]
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    default.save(OUT_ICO, format="ICO", sizes=sizes)
    print(f"Wrote {len(variants)} logos to {LOGOS}")
    print(f"Default icon: {OUT_ICO}")


if __name__ == "__main__":
    save_all()
