from __future__ import annotations

import customtkinter as ctk

from .branding import apply_window_icon
from .ui_text import make_scroll_textbox, refresh_scrollbar


class TranslationOverlay(ctk.CTkToplevel):
    """Always-on-top floating panel showing latest translation."""

    def __init__(self, master: ctk.CTk, opacity: float = 0.92) -> None:
        super().__init__(master)
        self.title("ScreenLingo")
        self.attributes("-topmost", True)
        self.attributes("-alpha", opacity)
        self.overrideredirect(True)
        self.geometry("420x320+40+40")
        self.configure(fg_color=("#1a1a2e", "#1a1a2e"))
        apply_window_icon(self)

        self._drag_x = 0
        self._drag_y = 0

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 0))
        self.status_label = ctk.CTkLabel(
            header, text="Live translation", font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(side="left")
        close_btn = ctk.CTkButton(header, text="×", width=28, height=28, command=self.withdraw)
        close_btn.pack(side="right")

        header.bind("<Button-1>", self._start_drag)
        header.bind("<B1-Motion>", self._on_drag)
        self.status_label.bind("<Button-1>", self._start_drag)
        self.status_label.bind("<B1-Motion>", self._on_drag)

        self.original_box = make_scroll_textbox(self, height=110)
        self.original_box.pack(fill="both", expand=True, padx=10, pady=6)
        self.original_box.configure(state="disabled", font=ctk.CTkFont(size=12))

        ctk.CTkLabel(self, text="Translation", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=12)
        self.translation_box = make_scroll_textbox(self, height=110)
        self.translation_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.translation_box.configure(state="disabled", font=ctk.CTkFont(size=13, weight="bold"))

        self.frequent_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11), text_color="#7fdbca", wraplength=380
        )
        self.frequent_label.pack(fill="x", padx=10, pady=(0, 8))

    def _start_drag(self, event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event) -> None:
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    def set_content(self, original: str, translated: str, frequent_hint: str = "") -> None:
        self._set_text(self.original_box, original or "(no text detected)")
        self._set_text(self.translation_box, translated or "—")
        self.frequent_label.configure(text=frequent_hint or "")

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    @staticmethod
    def _set_text(box: ctk.CTkTextbox, content: str) -> None:
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", content)
        box.configure(state="disabled")
        refresh_scrollbar(box)
