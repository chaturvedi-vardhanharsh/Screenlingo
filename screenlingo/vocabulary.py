from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import DB_PATH
from .lang_detect import detect_language, normalize_lang_code
from .translation_text import sanitize_translation
from .translator import translate_word


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WordEntry:
    id: int
    word: str
    translation: str
    source_lang: str
    target_lang: str
    seen_count: int
    correct_count: int
    wrong_count: int
    ease: float
    interval_days: int
    next_review: str | None
    first_seen: str
    last_seen: str


class VocabularyStore:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    translation TEXT NOT NULL DEFAULT '',
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    seen_count INTEGER NOT NULL DEFAULT 0,
                    correct_count INTEGER NOT NULL DEFAULT 0,
                    wrong_count INTEGER NOT NULL DEFAULT 0,
                    ease REAL NOT NULL DEFAULT 2.5,
                    interval_days INTEGER NOT NULL DEFAULT 0,
                    next_review TEXT,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    UNIQUE(word, source_lang, target_lang)
                );
                CREATE INDEX IF NOT EXISTS idx_words_seen ON words(seen_count DESC);
                CREATE INDEX IF NOT EXISTS idx_words_review ON words(next_review);
                """
            )

    def record_words(
        self,
        words: list[str],
        source_lang: str,
        target_lang: str,
        min_seen_for_learn: int = 2,
        *,
        context_text: str = "",
    ) -> list[str]:
        """Track words from OCR text. Returns newly frequent words worth highlighting."""
        if not words:
            return []
        source_lang = normalize_lang_code(source_lang)
        if source_lang == "auto" and context_text:
            detected = detect_language(context_text)
            if detected:
                source_lang = detected
        now = _now()
        new_frequent: list[str] = []
        with self._connect() as conn:
            for word in words:
                row = conn.execute(
                    "SELECT id, seen_count FROM words WHERE word=? AND source_lang=? AND target_lang=?",
                    (word, source_lang, target_lang),
                ).fetchone()
                if row:
                    new_count = row["seen_count"] + 1
                    conn.execute(
                        "UPDATE words SET seen_count=?, last_seen=? WHERE id=?",
                        (new_count, now, row["id"]),
                    )
                    if new_count == min_seen_for_learn:
                        new_frequent.append(word)
                else:
                    tr_src = source_lang if source_lang != "auto" else "auto"
                    try:
                        translation = translate_word(word, tr_src, target_lang)
                    except Exception:
                        translation = ""
                    conn.execute(
                        """
                        INSERT INTO words (word, translation, source_lang, target_lang,
                            seen_count, first_seen, last_seen, next_review)
                        VALUES (?, ?, ?, ?, 1, ?, ?, ?)
                        """,
                        (word, translation, source_lang, target_lang, now, now, now),
                    )
        return new_frequent

    def backfill_auto_source_languages(self, limit: int = 500) -> int:
        """Replace source_lang='auto' with detected language; merge duplicates."""
        updated = 0
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM words WHERE source_lang = 'auto' ORDER BY seen_count DESC LIMIT ?",
                (limit,),
            ).fetchall()
            for row in rows:
                sample = row["word"]
                if len(sample) < 4:
                    continue
                detected = detect_language(sample)
                if not detected or detected == "auto":
                    continue
                detected = normalize_lang_code(detected)
                conflict = conn.execute(
                    """
                    SELECT id, seen_count FROM words
                    WHERE word=? AND source_lang=? AND target_lang=? AND id!=?
                    """,
                    (row["word"], detected, row["target_lang"], row["id"]),
                ).fetchone()
                if conflict:
                    conn.execute(
                        "UPDATE words SET seen_count = seen_count + ? WHERE id = ?",
                        (row["seen_count"], conflict["id"]),
                    )
                    conn.execute("DELETE FROM words WHERE id = ?", (row["id"],))
                else:
                    conn.execute(
                        "UPDATE words SET source_lang = ? WHERE id = ?",
                        (detected, row["id"]),
                    )
                updated += 1
        return updated

    @staticmethod
    def _source_sql(source_lang: str) -> tuple[str, tuple[str, ...]]:
        """Match words saved with auto-detect or a specific source language."""
        if source_lang == "auto":
            return "source_lang = 'auto'", ()
        return "(source_lang = ? OR source_lang = 'auto')", (source_lang,)

    def repair_translations(self) -> int:
        """Clean tips/errors from stored translations. Returns rows updated."""
        updated = 0
        with self._connect() as conn:
            rows = conn.execute("SELECT id, translation FROM words").fetchall()
            for row in rows:
                clean = sanitize_translation(row["translation"] or "")
                if clean != (row["translation"] or ""):
                    conn.execute("UPDATE words SET translation=? WHERE id=?", (clean, row["id"]))
                    updated += 1
        return updated

    def ensure_translations(self, source_lang: str, target_lang: str, limit: int = 50) -> None:
        self.backfill_auto_source_languages()
        self.repair_translations()
        src_sql, src_params = self._source_sql(source_lang)
        tr_source = source_lang if source_lang != "auto" else "auto"
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT id, word, translation FROM words
                WHERE {src_sql} AND target_lang = ?
                  AND (translation = '' OR translation IS NULL OR translation LIKE '[%')
                ORDER BY seen_count DESC LIMIT ?
                """,
                (*src_params, target_lang, limit),
            ).fetchall()
            for row in rows:
                try:
                    tr = translate_word(row["word"], tr_source, target_lang)
                    if not tr:
                        continue
                    conn.execute("UPDATE words SET translation=? WHERE id=?", (tr, row["id"]))
                except Exception:
                    pass

    def list_language_pairs(self) -> list[tuple[str, str, int]]:
        """All (source, target) pairs in the database with word counts."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT source_lang, target_lang, COUNT(*) AS cnt
                FROM words
                GROUP BY source_lang, target_lang
                ORDER BY cnt DESC
                """
            ).fetchall()
        return [(r["source_lang"], r["target_lang"], int(r["cnt"])) for r in rows]

    def fetch_words(
        self,
        source_lang: str,
        target_lang: str,
        limit: int = 100,
        min_seen: int = 1,
    ) -> list[WordEntry]:
        src_sql, src_params = self._source_sql(source_lang)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM words
                WHERE {src_sql} AND target_lang = ?
                  AND seen_count >= ?
                ORDER BY seen_count DESC, word ASC
                LIMIT ?
                """,
                (*src_params, target_lang, min_seen, limit),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def top_words(self, source_lang: str, target_lang: str, limit: int = 30) -> list[WordEntry]:
        src_sql, src_params = self._source_sql(source_lang)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM words
                WHERE {src_sql} AND target_lang = ? AND seen_count >= 2
                ORDER BY seen_count DESC LIMIT ?
                """,
                (*src_params, target_lang, limit),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def due_for_review(self, source_lang: str, target_lang: str, limit: int = 20) -> list[WordEntry]:
        now = _now()
        src_sql, src_params = self._source_sql(source_lang)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM words
                WHERE {src_sql} AND target_lang = ?
                  AND seen_count >= 2
                  AND (next_review IS NULL OR next_review <= ?)
                ORDER BY seen_count DESC, next_review ASC
                LIMIT ?
                """,
                (*src_params, target_lang, now, limit),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def practice_words(
        self, source_lang: str, target_lang: str, limit: int = 20, min_seen: int = 1
    ) -> list[WordEntry]:
        """Words available to practice (broader than due_for_review for new users)."""
        src_sql, src_params = self._source_sql(source_lang)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM words
                WHERE {src_sql} AND target_lang = ? AND seen_count >= ?
                ORDER BY seen_count DESC, last_seen DESC
                LIMIT ?
                """,
                (*src_params, target_lang, min_seen, limit),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def record_review(self, word_id: int, knew_it: bool) -> None:
        """Simple SM-2 inspired spaced repetition."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM words WHERE id=?", (word_id,)).fetchone()
            if not row:
                return
            ease = row["ease"]
            interval = row["interval_days"]
            if knew_it:
                correct = row["correct_count"] + 1
                wrong = row["wrong_count"]
                if interval == 0:
                    interval = 1
                elif interval == 1:
                    interval = 3
                else:
                    interval = max(1, int(round(interval * ease)))
                ease = min(3.0, ease + 0.1)
            else:
                correct = row["correct_count"]
                wrong = row["wrong_count"] + 1
                interval = 1
                ease = max(1.3, ease - 0.2)
            from datetime import timedelta

            next_dt = datetime.now(timezone.utc) + timedelta(days=interval)
            conn.execute(
                """
                UPDATE words SET correct_count=?, wrong_count=?, ease=?, interval_days=?,
                    next_review=?, last_seen=?
                WHERE id=?
                """,
                (correct, wrong, ease, interval, next_dt.isoformat(), _now(), word_id),
            )

    def stats(self, source_lang: str, target_lang: str) -> dict:
        src_sql, src_params = self._source_sql(source_lang)
        with self._connect() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM words WHERE {src_sql} AND target_lang = ?",
                (*src_params, target_lang),
            ).fetchone()[0]
            frequent = conn.execute(
                f"SELECT COUNT(*) FROM words WHERE {src_sql} AND target_lang = ? AND seen_count >= 2",
                (*src_params, target_lang),
            ).fetchone()[0]
            mastered = conn.execute(
                f"SELECT COUNT(*) FROM words WHERE {src_sql} AND target_lang = ? AND correct_count >= 3",
                (*src_params, target_lang),
            ).fetchone()[0]
        return {"total": total, "frequent": frequent, "mastered": mastered}

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> WordEntry:
        return WordEntry(
            id=row["id"],
            word=row["word"],
            translation=row["translation"] or "",
            source_lang=row["source_lang"],
            target_lang=row["target_lang"],
            seen_count=row["seen_count"],
            correct_count=row["correct_count"],
            wrong_count=row["wrong_count"],
            ease=row["ease"],
            interval_days=row["interval_days"],
            next_review=row["next_review"],
            first_seen=row["first_seen"],
            last_seen=row["last_seen"],
        )
