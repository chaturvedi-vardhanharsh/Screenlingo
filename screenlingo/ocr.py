from __future__ import annotations

import asyncio
import re
import sys

from PIL import Image


def extract_text(image: Image.Image) -> str:
    """Run OCR on a PIL image and return normalized plain text."""
    if sys.platform != "win32":
        raise RuntimeError("ScreenLingo OCR requires Windows 10 or later")
    return normalize_text(asyncio.run(_windows_ocr_async(image)))


def _pil_to_software_bitmap(image: Image.Image):
    from winrt.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
    import winrt.windows.storage.streams as streams

    rgba = image.convert("RGBA")
    data_writer = streams.DataWriter()
    data_writer.write_bytes(rgba.tobytes())
    bitmap = SoftwareBitmap(BitmapPixelFormat.RGBA8, rgba.width, rgba.height)
    bitmap.copy_from_buffer(data_writer.detach_buffer())
    return bitmap


async def _windows_ocr_async(image: Image.Image) -> str:
    from winrt.windows.globalization import Language
    from winrt.windows.media.ocr import OcrEngine

    bitmap = _pil_to_software_bitmap(image)
    engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        engine = OcrEngine.try_create_from_language(Language("en"))
    if engine is None:
        raise RuntimeError("Windows OCR is not available for your language profile")

    result = await engine.recognize_async(bitmap)
    return result.text or ""


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize_words(text: str, min_length: int = 3) -> list[str]:
    words = re.findall(r"[\w']+", text, flags=re.UNICODE)
    return [w.lower() for w in words if len(w) >= min_length and not w.isdigit()]
