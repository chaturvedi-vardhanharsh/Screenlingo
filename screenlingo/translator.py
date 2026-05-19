from __future__ import annotations

import hashlib
from functools import lru_cache

import requests
from deep_translator import MyMemoryTranslator

from .config import language_label
from .learn_check import normalize_answer
from .ssl_setup import requests_verify_setting
from .text_utils import chunk_text, prepare_text_for_translation
from .translation_text import is_error_translation, sanitize_translation

_GOOGLE_API = "https://translate.googleapis.com/translate_a/single"


@lru_cache(maxsize=256)
def _cache_key(text: str, source: str, target: str) -> str:
    raw = f"{source}|{target}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


_translation_cache: dict[str, str] = {}


def clear_translation_cache() -> None:
    _translation_cache.clear()
    _cache_key.cache_clear()


def _base_lang(code: str) -> str:
    if not code or code == "auto":
        return ""
    return code.split("-")[0].lower()


def _langs_equivalent(source: str, target: str) -> bool:
    if source == "auto" or not source or not target:
        return False
    return _base_lang(source) == _base_lang(target)


def _google_translate_chunk(text: str, source: str, target: str) -> str:
    params = {
        "client": "gtx",
        "sl": source if source != "auto" else "auto",
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
    translator = MyMemoryTranslator(source=src, target=target)
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
    show_same_language_tip: bool = True,
) -> str:
    text = prepare_text_for_translation(text, max_chars=max_chars)
    if not text:
        return ""

    source_lang = source_lang or "auto"
    target_lang = target_lang or "en"

    if _langs_equivalent(source_lang, target_lang):
        label = language_label(target_lang)
        return (
            f"[Same language] Source and target are both {label}. "
            f"Change target language in the app (e.g. Hindi, Spanish)."
        )

    key = _cache_key(text, source_lang, target_lang)
    if key in _translation_cache:
        return _translation_cache[key]

    src = source_lang if source_lang != "auto" else "auto"
    try:
        parts = chunk_text(text)
        translated_parts = [_translate_chunk_with_fallback(part, src, target_lang) for part in parts]
        result = "\n".join(translated_parts)
        if (
            show_same_language_tip
            and result.strip().lower() == text.strip().lower()
            and target_lang != "auto"
            and source_lang == "auto"
        ):
            result = (
                f"{result}\n\n"
                f"[Tip] Text may already be {language_label(target_lang)}, "
                f"or translation was blocked. Try another target language or Relax SSL check."
            )
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


def translate_word(word: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    """Translate a single vocabulary word — never includes screen UI tips."""
    word = word.strip()
    if not word or _langs_equivalent(source_lang, target_lang):
        return ""
    src = source_lang if source_lang != "auto" else "auto"
    try:
        result = sanitize_translation(_translate_chunk_with_fallback(word, src, target_lang))
    except Exception:
        return ""
    if not result or is_error_translation(result):
        return ""
    if normalize_answer(result) == normalize_answer(word):
        return ""
    return result
