from __future__ import annotations

import customtkinter as ctk

from .config import format_lang_pair
from .translation_text import sanitize_translation
from .vocabulary import WordEntry


def pair_menu_label(source_lang: str, target_lang: str, count: int) -> str:
    return f"{format_lang_pair(source_lang, target_lang)} ({count} words)"


def mastery_label(entry: WordEntry) -> str:
    if entry.correct_count >= 3:
        return "Mastered"
    if entry.correct_count > 0:
        return "Learning"
    return "New"


def add_vocab_word_card(parent: ctk.CTkScrollableFrame, entry: WordEntry) -> None:
    """One comfortable vocabulary row (not log-style)."""
    card = ctk.CTkFrame(parent, corner_radius=10)
    card.pack(fill="x", padx=4, pady=6)

    header = ctk.CTkFrame(card, fg_color="transparent")
    header.pack(fill="x", padx=14, pady=(12, 4))

    ctk.CTkLabel(
        header,
        text=entry.word,
        font=ctk.CTkFont(size=18, weight="bold"),
        anchor="w",
    ).pack(side="left")

    ctk.CTkLabel(
        header,
        text=f"Seen {entry.seen_count}×",
        font=ctk.CTkFont(size=12),
        text_color="gray60",
    ).pack(side="right")

    translation = sanitize_translation(entry.translation) or "—"
    ctk.CTkLabel(
        card,
        text=translation,
        font=ctk.CTkFont(size=15),
        text_color="#7fdbca",
        anchor="w",
        wraplength=520,
        justify="left",
    ).pack(fill="x", padx=14, pady=(0, 8))

    footer = ctk.CTkFrame(card, fg_color="transparent")
    footer.pack(fill="x", padx=14, pady=(0, 12))

    pair = format_lang_pair(entry.source_lang, entry.target_lang)
    ctk.CTkLabel(
        footer,
        text=pair,
        font=ctk.CTkFont(size=11),
        text_color="gray55",
    ).pack(side="left")

    progress = f"{mastery_label(entry)} · Correct {entry.correct_count} · Practice {entry.wrong_count}"
    ctk.CTkLabel(
        footer,
        text=progress,
        font=ctk.CTkFont(size=11),
        text_color="gray60",
    ).pack(side="right")


def show_vocab_empty_state(parent: ctk.CTkScrollableFrame, message: str) -> None:
    ctk.CTkLabel(
        parent,
        text=message,
        font=ctk.CTkFont(size=14),
        text_color="gray60",
        wraplength=520,
        justify="left",
    ).pack(padx=20, pady=40, anchor="w")
