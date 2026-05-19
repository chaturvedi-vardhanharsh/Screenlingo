from __future__ import annotations

import tkinter as tk
from typing import Callable


class RegionSelector(tk.Toplevel):
    """Fullscreen translucent overlay to drag-select a screen region."""

    def __init__(
        self,
        master: tk.Misc,
        on_select: Callable[[tuple[int, int, int, int]], None],
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master)
        self.on_select = on_select
        self.on_cancel = on_cancel
        self._finished = False
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.25)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.configure(bg="black")
        self.cursor = "crosshair"
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self.canvas = tk.Canvas(self, cursor="crosshair", highlightthickness=0, bg="black")
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
            text="Drag to select capture area · Esc to cancel",
            fg="white",
            bg="black",
            font=("Segoe UI", 14),
        )
        hint.place(relx=0.5, rely=0.02, anchor="n")

    def _on_press(self, event: tk.Event) -> None:
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#00d4ff", width=2
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
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        left, top = min(x1, x2), min(y1, y2)
        width, height = abs(x2 - x1), abs(y2 - y1)
        if width < 20 or height < 20:
            self._cancel()
            return
        self._complete((left, top, width, height))
