from __future__ import annotations

import tkinter as tk
from typing import Callable

from .dpi import enable_dpi_awareness, get_virtual_screen_bounds


class RegionSelector(tk.Toplevel):
    """Fullscreen translucent overlay to drag-select a screen region."""

    def __init__(
        self,
        master: tk.Misc,
        on_select: Callable[[tuple[int, int, int, int]], None],
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        enable_dpi_awareness()
        super().__init__(master)
        self.on_select = on_select
        self.on_cancel = on_cancel
        self._finished = False

        self._screen_left, self._screen_top, self._screen_width, self._screen_height = (
            get_virtual_screen_bounds()
        )

        # Do not use -fullscreen (sizes to parent window). Cover all monitors explicitly.
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.3)
        self.geometry(
            f"{self._screen_width}x{self._screen_height}"
            f"+{self._screen_left}+{self._screen_top}"
        )
        self.configure(bg="black")
        self.cursor = "crosshair"
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self.canvas = tk.Canvas(
            self,
            width=self._screen_width,
            height=self._screen_height,
            cursor="crosshair",
            highlightthickness=0,
            bg="black",
        )
        self.canvas.pack(fill="both", expand=True)

        self.start_x: int | None = None
        self.start_y: int | None = None
        self.rect_id: int | None = None

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", lambda _: self._cancel())

        hint = tk.Label(
            self,
            text="Drag anywhere on screen to select · Esc to cancel",
            fg="white",
            bg="black",
            font=("Segoe UI", 14),
        )
        hint.place(relx=0.5, y=12, anchor="n")

    def _to_screen_region(self, x1: int, y1: int, x2: int, y2: int) -> tuple[int, int, int, int]:
        left = self._screen_left + min(x1, x2)
        top = self._screen_top + min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        return left, top, width, height

    def _on_press(self, event: tk.Event) -> None:
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#00d4ff", width=3
        )

    def _on_drag(self, event: tk.Event) -> None:
        if self.rect_id is not None and self.start_x is not None:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def _cancel(self) -> None:
        if self._finished:
            return
        self._finished = True
        self.destroy()
        if self.on_cancel:
            self.on_cancel()

    def _complete(self, region: tuple[int, int, int, int]) -> None:
        if self._finished:
            return
        self._finished = True
        self.destroy()
        self.on_select(region)

    def _on_release(self, event: tk.Event) -> None:
        if self.start_x is None or self.start_y is None:
            self._cancel()
            return
        region = self._to_screen_region(self.start_x, self.start_y, event.x, event.y)
        if region[2] < 20 or region[3] < 20:
            self._cancel()
            return
        self._complete(region)
