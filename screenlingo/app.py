from __future__ import annotations

import re
import threading
import tkinter as tk

import customtkinter as ctk

from .config import DEFAULT_LANGUAGES, AppConfig, language_label
from .translator import clear_translation_cache
from .engine import LiveTranslationEngine
from .overlay import TranslationOverlay
from .region_select import RegionSelector
from .vocabulary import VocabularyStore, WordEntry

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _base_lang_code(code: str) -> str:
    return code.split("-")[0].lower() if code and code != "auto" else ""


class ScreenLingoApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ScreenLingo — Real-time Screen Translator")
        self.geometry("720x640")
        self.minsize(640, 560)

        self.config_data = AppConfig.load()
        self.vocabulary = VocabularyStore()
        self.engine = LiveTranslationEngine(
            self.config_data,
            self.vocabulary,
            on_update=self._on_translation_update,
            on_status=self._on_status,
        )
        self.overlay: TranslationOverlay | None = None
        self._review_queue: list[WordEntry] = []
        self._review_index = 0
        self._card_revealed = False

        self._build_ui()
        self._setup_hotkeys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_live = self.tabview.add("Live Translate")
        self.tab_learn = self.tabview.add("Learn Words")
        self.tab_vocab = self.tabview.add("My Vocabulary")

        self._build_live_tab()
        self._build_learn_tab()
        self._build_vocab_tab()

    def _lang_menu(self, parent, variable: ctk.StringVar, include_auto: bool = False) -> ctk.CTkOptionMenu:
        codes = list(DEFAULT_LANGUAGES.keys())
        if not include_auto:
            codes = [c for c in codes if c != "auto"]
        labels = [f"{language_label(c)} ({c})" for c in codes]
        self._lang_label_to_code = getattr(self, "_lang_label_to_code", {})
        for lbl, code in zip(labels, codes):
            self._lang_label_to_code[lbl] = code

        def on_change(choice: str) -> None:
            variable.set(self._lang_label_to_code.get(choice, codes[0]))
            self._update_lang_status()

        current = variable.get()
        menu = ctk.CTkOptionMenu(
            parent,
            values=labels,
            command=on_change,
        )
        for lbl, code in zip(labels, codes):
            if code == current:
                menu.set(lbl)
                break
        return menu

    @staticmethod
    def _code_from_menu_label(label: str) -> str:
        match = re.search(r"\(([a-z]{2}(?:-[A-Z]{2})?)\)\s*$", label)
        return match.group(1) if match else label

    def _read_lang_from_menu(self, menu: ctk.CTkOptionMenu, fallback_var: ctk.StringVar) -> str:
        try:
            label = menu.get()
            return self._lang_label_to_code.get(label, self._code_from_menu_label(label))
        except Exception:
            return fallback_var.get()

    def _update_lang_status(self) -> None:
        src = language_label(self.src_var.get())
        tgt = language_label(self.tgt_var.get())
        note = ""
        if self.src_var.get() != "auto" and _base_lang_code(self.src_var.get()) == _base_lang_code(
            self.tgt_var.get()
        ):
            note = " · Change target language — source and target are the same"
        self.lang_status_label.configure(text=f"Translating: {src} → {tgt}{note}")

    def _build_live_tab(self) -> None:
        frame = self.tab_live

        settings = ctk.CTkFrame(frame)
        settings.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(settings, text="Source language").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.src_var = ctk.StringVar(value=self.config_data.source_lang)
        self.src_menu = self._lang_menu(settings, self.src_var, include_auto=True)
        self.src_menu.grid(row=0, column=1, padx=8, pady=8)

        ctk.CTkLabel(settings, text="Target language").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.tgt_var = ctk.StringVar(value=self.config_data.target_lang)
        self.tgt_menu = self._lang_menu(settings, self.tgt_var)
        self.tgt_menu.grid(row=1, column=1, padx=8, pady=8)

        self.lang_status_label = ctk.CTkLabel(
            settings,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#7fdbca",
        )
        self.lang_status_label.grid(row=2, column=0, columnspan=2, padx=8, pady=(0, 4), sticky="w")
        self._update_lang_status()

        ctk.CTkLabel(settings, text="Refresh (seconds)").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.interval_slider = ctk.CTkSlider(settings, from_=1, to=8, number_of_steps=7)
        self.interval_slider.set(self.config_data.poll_interval_sec)
        self.interval_slider.grid(row=3, column=1, padx=8, pady=8, sticky="ew")
        settings.grid_columnconfigure(1, weight=1)

        region_row = ctk.CTkFrame(frame, fg_color="transparent")
        region_row.pack(fill="x", padx=8, pady=4)
        self.region_label = ctk.CTkLabel(region_row, text=self._region_text())
        self.region_label.pack(side="left", padx=8)
        ctk.CTkButton(region_row, text="Select screen area", command=self._pick_region).pack(
            side="left", padx=4
        )
        ctk.CTkButton(region_row, text="Full screen", command=self._clear_region).pack(side="left", padx=4)

        net = ctk.CTkFrame(frame)
        net.pack(fill="x", padx=8, pady=4)
        self.system_cert_var = ctk.BooleanVar(value=self.config_data.use_system_certificates)
        self.relax_ssl_var = ctk.BooleanVar(value=not self.config_data.ssl_verify)
        ctk.CTkCheckBox(
            net,
            text="Use Windows certificates (recommended on work PC)",
            variable=self.system_cert_var,
            command=self._apply_settings,
        ).pack(anchor="w", padx=8, pady=2)
        ctk.CTkCheckBox(
            net,
            text="Relax SSL check (only if translation still fails on corporate network)",
            variable=self.relax_ssl_var,
            command=self._apply_settings,
        ).pack(anchor="w", padx=8, pady=2)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=12)
        self.live_btn = ctk.CTkButton(
            btn_row, text="Start live translation", command=self._toggle_live, height=40
        )
        self.live_btn.pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Translate now", command=self._translate_once, height=40).pack(
            side="left", padx=4
        )
        ctk.CTkButton(btn_row, text="Show overlay", command=self._show_overlay, height=40).pack(
            side="left", padx=4
        )

        self.status_label = ctk.CTkLabel(frame, text="Ready", text_color="gray70")
        self.status_label.pack(anchor="w", padx=12)

        preview = ctk.CTkFrame(frame)
        preview.pack(fill="both", expand=True, padx=8, pady=8)
        ctk.CTkLabel(preview, text="Detected text").pack(anchor="w", padx=8, pady=(8, 0))
        self.preview_original = ctk.CTkTextbox(preview, height=120)
        self.preview_original.pack(fill="both", expand=True, padx=8, pady=4)
        ctk.CTkLabel(preview, text="Translation").pack(anchor="w", padx=8)
        self.preview_translated = ctk.CTkTextbox(preview, height=120)
        self.preview_translated.pack(fill="both", expand=True, padx=8, pady=8)

        hint = ctk.CTkLabel(
            frame,
            text=f"Tip: use Select screen area (not full screen) to avoid translating this app. "
            f"Hotkeys: {self.config_data.hotkey_capture} / {self.config_data.hotkey_toggle_live}",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            wraplength=660,
        )
        hint.pack(pady=4)

    def _build_learn_tab(self) -> None:
        frame = self.tab_learn
        self.learn_stats = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=13))
        self.learn_stats.pack(pady=8)

        card = ctk.CTkFrame(frame)
        card.pack(fill="both", expand=True, padx=16, pady=8)
        self.card_word = ctk.CTkLabel(
            card, text="Press Start to practice frequent words", font=ctk.CTkFont(size=28, weight="bold")
        )
        self.card_word.pack(pady=24)
        self.card_translation = ctk.CTkLabel(
            card, text="", font=ctk.CTkFont(size=20), text_color="#7fdbca"
        )
        self.card_translation.pack(pady=8)
        self.card_meta = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12), text_color="gray60")
        self.card_meta.pack(pady=4)

        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(pady=12)
        ctk.CTkButton(actions, text="Start session", command=self._start_learn_session).pack(
            side="left", padx=6
        )
        ctk.CTkButton(actions, text="Reveal", command=self._reveal_card).pack(side="left", padx=6)
        ctk.CTkButton(actions, text="I knew it", command=lambda: self._rate_card(True), fg_color="#2d6a4f").pack(
            side="left", padx=6
        )
        ctk.CTkButton(actions, text="Still learning", command=lambda: self._rate_card(False), fg_color="#9d0208").pack(
            side="left", padx=6
        )

    def _build_vocab_tab(self) -> None:
        frame = self.tab_vocab
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(top, text="Refresh list", command=self._refresh_vocab_list).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Fill missing translations", command=self._fill_translations).pack(
            side="left", padx=4
        )
        self.vocab_box = ctk.CTkTextbox(frame)
        self.vocab_box.pack(fill="both", expand=True, padx=8, pady=8)
        self._refresh_vocab_list()

    def _region_text(self) -> str:
        r = self.config_data.capture_region
        if r is None:
            return "Capture: full screen"
        return f"Capture region: {r[0]}×{r[1]} +{r[2]}×{r[3]}"

    def _pick_region(self) -> None:
        self._hide_for_region_select()

        def restore() -> None:
            self._show_after_region_select()

        def on_select(region: tuple[int, int, int, int]) -> None:
            self.config_data.capture_region = region
            self.config_data.save()
            self.region_label.configure(text=self._region_text())
            restore()

        def open_selector() -> None:
            selector = RegionSelector(self, on_select, on_cancel=restore)
            selector.lift()
            selector.focus_force()
            try:
                selector.grab_set()
            except tk.TclError:
                pass

        # Brief delay so the main window is fully hidden before the overlay appears
        self.after(120, open_selector)

    def _hide_for_region_select(self) -> None:
        self._overlay_was_visible = False
        if self.overlay is not None and self.overlay.winfo_exists():
            try:
                if self.overlay.state() != "withdrawn":
                    self._overlay_was_visible = True
                    self.overlay.withdraw()
            except tk.TclError:
                pass
        self.withdraw()
        self.update_idletasks()

    def _show_after_region_select(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        if self._overlay_was_visible and self.overlay is not None and self.overlay.winfo_exists():
            self.overlay.deiconify()
            self.overlay.lift()

    def _clear_region(self) -> None:
        self.config_data.capture_region = None
        self.config_data.save()
        self.region_label.configure(text=self._region_text())

    def _apply_settings(self) -> None:
        prev_src = self.config_data.source_lang
        prev_tgt = self.config_data.target_lang
        self.config_data.source_lang = self._read_lang_from_menu(self.src_menu, self.src_var)
        self.config_data.target_lang = self._read_lang_from_menu(self.tgt_menu, self.tgt_var)
        self.src_var.set(self.config_data.source_lang)
        self.tgt_var.set(self.config_data.target_lang)
        self.config_data.poll_interval_sec = float(self.interval_slider.get())
        self.config_data.use_system_certificates = bool(self.system_cert_var.get())
        self.config_data.ssl_verify = not bool(self.relax_ssl_var.get())
        self.config_data.save()
        if prev_src != self.config_data.source_lang or prev_tgt != self.config_data.target_lang:
            clear_translation_cache()
        self._update_lang_status()
        self._reconfigure_ssl()

    def _reconfigure_ssl(self) -> None:
        from .ssl_setup import configure_ssl, patch_requests

        configure_ssl(
            use_system_certificates=self.config_data.use_system_certificates,
            ssl_verify=self.config_data.ssl_verify,
        )
        patch_requests()

    def _show_overlay(self) -> None:
        if self.overlay is None or not self.overlay.winfo_exists():
            self.overlay = TranslationOverlay(self, self.config_data.overlay_opacity)
        self.overlay.deiconify()
        self.overlay.lift()

    def _on_translation_update(self, original: str, translated: str, new_freq: list[str]) -> None:
        def ui() -> None:
            self._set_preview(original, translated)
            hint = ""
            if new_freq:
                hint = "New frequent words: " + ", ".join(new_freq[:8])
            if self.overlay and self.overlay.winfo_exists():
                self.overlay.set_content(original, translated, hint)
            self._on_status("Updated")

        self.after(0, ui)

    def _on_status(self, msg: str) -> None:
        self.after(0, lambda: self.status_label.configure(text=msg))

    def _set_preview(self, original: str, translated: str) -> None:
        for box, content in (
            (self.preview_original, original),
            (self.preview_translated, translated),
        ):
            box.delete("1.0", "end")
            box.insert("1.0", content)

    def _translate_once(self) -> None:
        self._apply_settings()

        def work() -> None:
            try:
                text, translated, new_freq = self.engine.capture_once()
                if text:
                    self._on_translation_update(text, translated, new_freq)
                else:
                    self._on_status("No text detected — try a clearer region")
            except Exception as exc:
                self._on_status(str(exc))

        threading.Thread(target=work, daemon=True).start()

    def _toggle_live(self) -> None:
        self._apply_settings()
        if self.engine.is_running:
            self.engine.stop()
            self.live_btn.configure(text="Start live translation")
            self._on_status("Live translation stopped")
        else:
            self._show_overlay()
            self.engine.start()
            self.live_btn.configure(text="Stop live translation")
            self._on_status("Live translation running…")

    def _setup_hotkeys(self) -> None:
        try:
            import keyboard

            keyboard.add_hotkey(self.config_data.hotkey_capture, lambda: self.after(0, self._translate_once))
            keyboard.add_hotkey(self.config_data.hotkey_toggle_live, lambda: self.after(0, self._toggle_live))
        except Exception:
            pass

    def _start_learn_session(self) -> None:
        self._apply_settings()
        src = self.config_data.source_lang
        tgt = self.config_data.target_lang
        self.vocabulary.ensure_translations(src, tgt)
        self._review_queue = self.vocabulary.due_for_review(src, tgt, limit=self.config_data.learn_daily_goal)
        self._review_index = 0
        self._card_revealed = False
        stats = self.vocabulary.stats(src, tgt)
        self.learn_stats.configure(
            text=f"Words tracked: {stats['total']} · Frequent: {stats['frequent']} · Mastered: {stats['mastered']}"
        )
        self._show_current_card()

    def _show_current_card(self) -> None:
        if self._review_index >= len(self._review_queue):
            self.card_word.configure(text="Session complete!")
            self.card_translation.configure(text="Come back later for more reviews.")
            self.card_meta.configure(text="")
            return
        entry = self._review_queue[self._review_index]
        self._card_revealed = False
        self.card_word.configure(text=entry.word)
        self.card_translation.configure(text="?")
        self.card_meta.configure(
            text=f"Seen {entry.seen_count}× on your screen · {self._review_index + 1}/{len(self._review_queue)}"
        )

    def _reveal_card(self) -> None:
        if self._review_index >= len(self._review_queue):
            return
        entry = self._review_queue[self._review_index]
        self._card_revealed = True
        self.card_translation.configure(text=entry.translation or "(no translation)")

    def _rate_card(self, knew_it: bool) -> None:
        if self._review_index >= len(self._review_queue):
            return
        if not self._card_revealed:
            self._reveal_card()
            return
        entry = self._review_queue[self._review_index]
        self.vocabulary.record_review(entry.id, knew_it)
        self._review_index += 1
        self._show_current_card()

    def _refresh_vocab_list(self) -> None:
        self._apply_settings()
        words = self.vocabulary.top_words(
            self.config_data.source_lang, self.config_data.target_lang, limit=50
        )
        lines = ["Word | Translation | Times seen | Reviews\n" + "-" * 55 + "\n"]
        for w in words:
            lines.append(
                f"{w.word} | {w.translation or '—'} | {w.seen_count} | ✓{w.correct_count} ✗{w.wrong_count}\n"
            )
        if len(lines) == 1:
            lines.append("\nNo frequent words yet. Use live translate — words appear after you see them twice.")
        self.vocab_box.delete("1.0", "end")
        self.vocab_box.insert("1.0", "".join(lines))

    def _fill_translations(self) -> None:
        self._apply_settings()

        def work() -> None:
            self.vocabulary.ensure_translations(
                self.config_data.source_lang, self.config_data.target_lang
            )
            self.after(0, self._refresh_vocab_list)

        threading.Thread(target=work, daemon=True).start()

    def _on_close(self) -> None:
        self.engine.stop()
        self.destroy()


def run() -> None:
    from .bootstrap import init_app

    init_app()
    app = ScreenLingoApp()
    app.mainloop()
