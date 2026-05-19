from __future__ import annotations

import re


def prepare_text_for_translation(text: str, max_chars: int = 1200) -> str:
    """Trim OCR noise and limit length so translation APIs stay reliable."""
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Skip very long lines that are mostly URLs / encoded junk
        if len(line) > 120 and (
            "http://" in line.lower()
            or "https://" in line.lower()
            or line.count("%") > 8
        ):
            continue
        if len(line) > 300:
            line = line[:300] + "…"
        lines.append(line)

    cleaned = "\n".join(lines).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rsplit("\n", 1)[0].strip() or cleaned[:max_chars]


def chunk_text(text: str, chunk_size: int = 450) -> list[str]:
    """Split text into API-friendly chunks (paragraph-aware)."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in re.split(r"\n+", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) > chunk_size:
            if current:
                chunks.append("\n".join(current))
                current, current_len = [], 0
            for i in range(0, len(paragraph), chunk_size):
                chunks.append(paragraph[i : i + chunk_size])
            continue
        add_len = len(paragraph) + (1 if current else 0)
        if current_len + add_len > chunk_size and current:
            chunks.append("\n".join(current))
            current, current_len = [paragraph], len(paragraph)
        else:
            current.append(paragraph)
            current_len += add_len

    if current:
        chunks.append("\n".join(current))
    return chunks
