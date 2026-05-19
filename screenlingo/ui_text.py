from __future__ import annotations

import customtkinter as ctk


def make_scroll_textbox(
    parent,
    *,
    height: int = 140,
    placeholder: str = "",
) -> ctk.CTkTextbox:
    """Text area with vertical scrollbar always visible (long OCR / translations)."""
    box = ctk.CTkTextbox(
        parent,
        height=height,
        wrap="word",
        activate_scrollbars=True,
    )
    if placeholder:
        box.insert("1.0", placeholder)
        box.configure(state="disabled")

    def _show_scrollbar() -> None:
        try:
            box._hide_y_scrollbar = False
            box._create_grid_for_text_and_scrollbars(re_grid_y_scrollbar=True)
            box.update_idletasks()
        except Exception:
            pass

    box.after(50, _show_scrollbar)
    box._force_scrollbar = _show_scrollbar
    return box


def refresh_scrollbar(textbox: ctk.CTkTextbox) -> None:
    if hasattr(textbox, "_force_scrollbar"):
        textbox.after(10, textbox._force_scrollbar)
    elif hasattr(textbox, "_check_if_scrollbars_needed"):
        textbox.after(10, textbox._check_if_scrollbars_needed)
