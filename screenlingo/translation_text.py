from __future__ import annotations

import re


def sanitize_translation(text: str) -> str:
    """Strip UI tips/errors from text saved or shown as a word translation."""
    if not text:
        return ""
    text = text.strip()
    for marker in ("[Tip]", "[Translation error", "[Same language]"):
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].strip()
    # Single-word entries should not include extra paragraphs
    if "\n" in text:
        text = text.split("\n")[0].strip()
    return text


def is_error_translation(text: str) -> bool:
    t = (text or "").strip()
    return not t or t.startswith("[")


def is_noop_translation(word: str, translation: str) -> bool:
    """True when translation adds no learning value (e.g. English → English)."""
    clean = sanitize_translation(translation)
    if not clean or is_error_translation(clean):
        return True
    return clean.casefold() == (word or "").strip().casefold()
