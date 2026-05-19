from __future__ import annotations

import hashlib
from functools import lru_cache

from deep_translator import GoogleTranslator


@lru_cache(maxsize=256)
def _cache_key(text: str, source: str, target: str) -> str:
    raw = f"{source}|{target}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


_translation_cache: dict[str, str] = {}


def translate_text(text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    text = text.strip()
    if not text:
        return ""
    key = _cache_key(text, source_lang, target_lang)
    if key in _translation_cache:
        return _translation_cache[key]
    src = source_lang if source_lang != "auto" else "auto"
    try:
        result = GoogleTranslator(source=src, target=target_lang).translate(text)
    except Exception as exc:
        result = f"[Translation error: {exc}]"
    _translation_cache[key] = result
    if len(_translation_cache) > 500:
        _translation_cache.clear()
    return result


def translate_word(word: str, source_lang: str, target_lang: str) -> str:
    return translate_text(word, source_lang, target_lang)
