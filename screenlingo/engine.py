from __future__ import annotations

import threading
import time
from typing import Callable

from .capture import capture_from_config
from .config import AppConfig
from .ocr import extract_text, tokenize_words
from .translator import translate_text
from .vocabulary import VocabularyStore


class LiveTranslationEngine:
    """Background loop: capture → OCR → translate → vocabulary."""

    def __init__(
        self,
        config: AppConfig,
        vocabulary: VocabularyStore,
        on_update: Callable[[str, str, list[str]], None],
        on_status: Callable[[str], None],
    ) -> None:
        self.config = config
        self.vocabulary = vocabulary
        self.on_update = on_update
        self.on_status = on_status
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_text_hash = ""

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def capture_once(self) -> tuple[str, str, list[str]]:
        self.on_status("Capturing…")
        image = capture_from_config(self.config)
        self.on_status("Reading text…")
        text = extract_text(image)
        if not text:
            return "", "", []
        self.on_status("Translating…")
        translated = translate_text(
            text,
            self.config.source_lang,
            self.config.target_lang,
            max_chars=self.config.max_translate_chars,
        )
        words = tokenize_words(text, self.config.min_word_length)
        src = self.config.source_lang if self.config.source_lang != "auto" else "auto"
        new_freq = self.vocabulary.record_words(
            words, src, self.config.target_lang
        )
        return text, translated, new_freq

    def _loop(self) -> None:
        while self._running:
            try:
                text, translated, new_freq = self.capture_once()
                if text:
                    h = hash(text)
                    if h != self._last_text_hash:
                        self._last_text_hash = h
                        self.on_update(text, translated, new_freq)
                else:
                    self.on_status("No text on screen")
            except Exception as exc:
                self.on_status(f"Error: {exc}")
            time.sleep(self.config.poll_interval_sec)
