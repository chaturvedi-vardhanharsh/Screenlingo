from __future__ import annotations

import re
import unicodedata


def normalize_answer(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.strip().lower())
    text = re.sub(r"\s+", " ", text)
    return text


def answers_match(user_answer: str, expected: str) -> bool:
    user = normalize_answer(user_answer)
    expected_n = normalize_answer(expected)
    if not user or not expected_n:
        return False
    if user == expected_n:
        return True
    # Ignore light punctuation differences
    strip_punct = lambda s: re.sub(r"[^\w\s]", "", s, flags=re.UNICODE)
    return strip_punct(user) == strip_punct(expected_n)


def is_valid_flashcard(word: str, translation: str) -> bool:
    """Skip cards where prompt and answer are the same."""
    if not word or not translation:
        return False
    if translation.startswith("["):
        return False
    return normalize_answer(word) != normalize_answer(translation)
