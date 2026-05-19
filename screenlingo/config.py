from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

APP_DIR = Path.home() / ".screenlingo"
CONFIG_PATH = APP_DIR / "config.json"
DB_PATH = APP_DIR / "vocabulary.db"

DEFAULT_LANGUAGES = {
    "auto": "Auto-detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
}


@dataclass
class AppConfig:
    source_lang: str = "auto"
    target_lang: str = "en"
    poll_interval_sec: float = 2.0
    capture_region: tuple[int, int, int, int] | None = None  # left, top, width, height
    overlay_opacity: float = 0.92
    min_word_length: int = 3
    learn_daily_goal: int = 10
    hotkey_capture: str = "ctrl+shift+t"
    hotkey_toggle_live: str = "ctrl+shift+l"
    max_translate_chars: int = 1200
    use_system_certificates: bool = True
    ssl_verify: bool = True

    def save(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> "AppConfig":
        if not CONFIG_PATH.exists():
            cfg = cls()
            cfg.save()
            return cfg
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        region = data.get("capture_region")
        if region is not None:
            data["capture_region"] = tuple(region)
        valid = {f.name for f in fields(cls)}
        data = {k: v for k, v in data.items() if k in valid}
        return cls(**data)


def language_label(code: str) -> str:
    return DEFAULT_LANGUAGES.get(code, code)
