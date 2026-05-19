from __future__ import annotations

import requests

from .config import DEFAULT_LANGUAGES
from .ssl_setup import requests_verify_setting

_GOOGLE_DETECT_URL = "https://translate.googleapis.com/translate_a/single"

# Map Google detect codes to our language keys
_GOOGLE_TO_APP: dict[str, str] = {
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-tw": "zh-TW",
}


def normalize_lang_code(code: str | None) -> str:
    if not code or code == "auto":
        return "auto"
    raw = code.strip()
    if raw in DEFAULT_LANGUAGES:
        return raw
    key = raw.lower().replace("_", "-")
    if key in _GOOGLE_TO_APP:
        return _GOOGLE_TO_APP[key]
    if key in DEFAULT_LANGUAGES:
        return key
    # Keep short ISO-style codes (e.g. sv, no, da)
    if len(key) <= 8 and key.replace("-", "").isalpha():
        return key if "-" in key else key
    return raw


def detect_language(text: str, *, sample_chars: int = 500) -> str | None:
    """
    Detect language of text using Google Translate (same client as translation).
    Returns app language code (e.g. sv, en) or None if detection fails.
    """
    text = (text or "").strip()
    if len(text) < 3:
        return None
    sample = text[:sample_chars]
    try:
        response = requests.get(
            _GOOGLE_DETECT_URL,
            params={
                "client": "gtx",
                "sl": "auto",
                "tl": "en",
                "dt": "t",
                "q": sample,
            },
            timeout=15,
            verify=requests_verify_setting(),
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 2 and data[2]:
            return normalize_lang_code(str(data[2]))
    except Exception:
        pass
    return None


def resolve_source_lang(configured_source: str, text: str) -> str:
    """Use configured source, or detect from OCR/screen text when set to auto."""
    if configured_source and configured_source != "auto":
        return normalize_lang_code(configured_source)
    detected = detect_language(text)
    return detected or "auto"
