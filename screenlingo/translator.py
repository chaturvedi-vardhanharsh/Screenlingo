from __future__ import annotations

import hashlib
from functools import lru_cache

import requests
from deep_translator import MyMemoryTranslator

from .ssl_setup import requests_verify_setting
from .text_utils import chunk_text, prepare_text_for_translation

# JSON endpoint — often works better than translate.google.com/m on corporate networks
_GOOGLE_API = "https://translate.googleapis.com/translate_a/single"


@lru_cache(maxsize=256)
def _cache_key(text: str, source: str, target: str) -> str:
    raw = f"{source}|{target}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


_translation_cache: dict[str, str] = {}


def _google_translate_chunk(text: str, source: str, target: str) -> str:
    params = {
        "client": "gtx",
        "sl": source,
        "tl": target,
        "dt": "t",
        "q": text,
    }
    response = requests.get(
        _GOOGLE_API,
        params=params,
        timeout=20,
        verify=requests_verify_setting(),
    )
    response.raise_for_status()
    data = response.json()
    if not data or not data[0]:
        raise ValueError("Empty translation response")
    return "".join(part[0] for part in data[0] if part and part[0])


def _mymemory_translate_chunk(text: str, source: str, target: str) -> str:
    src = "en" if source in ("auto", "") else source
    tgt = target or "en"
    translator = MyMemoryTranslator(source=src, target=tgt)
    return str(translator.translate(text))


def _translate_chunk_with_fallback(text: str, source: str, target: str) -> str:
    try:
        return _google_translate_chunk(text, source, target)
    except Exception:
        return _mymemory_translate_chunk(text, source, target)


def translate_text(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "en",
    *,
    max_chars: int = 1200,
) -> str:
    text = prepare_text_for_translation(text, max_chars=max_chars)
    if not text:
        return ""

    key = _cache_key(text, source_lang, target_lang)
    if key in _translation_cache:
        return _translation_cache[key]

    src = source_lang if source_lang != "auto" else "auto"
    try:
        parts = chunk_text(text)
        translated_parts = [_translate_chunk_with_fallback(part, src, target_lang) for part in parts]
        result = "\n".join(translated_parts)
    except Exception as exc:
        hint = ""
        err = str(exc).lower()
        if "certificate" in err or "ssl" in err:
            hint = " Try enabling Windows certificates or Relax SSL check in settings."
        elif "connection" in err or "resolve" in err:
            hint = " Check VPN or company network access."
        result = f"[Translation error: {exc}.{hint}]"

    _translation_cache[key] = result
    if len(_translation_cache) > 500:
        _translation_cache.clear()
    return result


def translate_word(word: str, source_lang: str, target_lang: str) -> str:
    return translate_text(word, source_lang, target_lang, max_chars=200)
