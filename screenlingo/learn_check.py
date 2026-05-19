from __future__ import annotations

import re
import unicodedata

from .translation_text import is_error_translation, is_noop_translation, sanitize_translation


def normalize_answer(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.strip().lower())
    text = re.sub(r"\s+", " ", text)
    return text


def answers_match(user_answer: str, expected: str) -> bool:
    user = normalize_answer(user_answer)
    expected_n = normalize_answer(sanitize_translation(expected))
    if not user or not expected_n:
        return False
    if user == expected_n:
        return True
    strip_punct = lambda s: re.sub(r"[^\w\s]", "", s, flags=re.UNICODE)
    return strip_punct(user) == strip_punct(expected_n)


def is_valid_flashcard(word: str, translation: str) -> bool:
    """Skip cards with missing, error, or identical translations."""
    if is_noop_translation(word, translation):
        return False
    clean = sanitize_translation(translation)
    return bool(clean) and not is_error_translation(clean)
