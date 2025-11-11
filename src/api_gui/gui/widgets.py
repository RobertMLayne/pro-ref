from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import json
import tkinter as tk
from tkinter import ttk

# ttkbootstrap.tooltip is deprecated; the widgets namespace exposes ToolTip.
from ttkbootstrap.widgets import ToolTip

__all__ = ["PillBar", "FacetsPanel", "TourOverlay", "TooltipLib"]


class PillBar(ttk.Frame):
    """Display active filters as removable pills."""

    def __init__(
        self,
        master: tk.Misc,
        on_remove: Callable[[str, str], None],
    ) -> None:
        super().__init__(master)
        self._on_remove = on_remove
        self._pills: list[ttk.Button] = []

    def set_filters(self, filters: Sequence[tuple[str, str]]) -> None:
        """Render the current filters as pill buttons."""

        for widget in self.winfo_children():
            widget.destroy()
        self._pills.clear()

        for name, value in filters:
            pill = ttk.Button(
                self,
                text=f"{name}: {value} ✕",
                command=lambda n=name, v=value: self._on_remove(n, v),
            )
            pill.pack(side="left", padx=2, pady=2)
            self._pills.append(pill)


class FacetsPanel(ttk.Frame):
    """Show available facets and allow selection via double-click."""

    def __init__(
        self,
        master: tk.Misc,
        on_select: Callable[[str, str], None],
    ) -> None:
        super().__init__(master)
        self._on_select = on_select
        self._tree = ttk.Treeview(
            self,
            columns=("value", "count"),
            show="tree headings",
            height=10,
        )
        self._tree.heading("#0", text="Field")
        self._tree.heading("value", text="Value")
        self._tree.heading("count", text="Count")
        self._tree.pack(fill="both", expand=True)
        self._tree.tag_bind("facet", "<Double-1>", self._on_double_click)

    def set_facets(
        self,
        facets: Mapping[str, Sequence[Mapping[str, object]]] | None,
    ) -> None:
        """Fill the tree with facet data from the current response."""

        self._tree.delete(*self._tree.get_children())
        if not facets:
            return

        for field, buckets in facets.items():
            parent = self._tree.insert("", "end", text=field, open=True)
            for bucket in buckets:
                value = bucket.get("value", "")
                count = bucket.get("count", 0)
                node = self._tree.insert(
                    parent,
                    "end",
                    text="",
                    values=(value, count),
                )
                self._tree.item(node, tags=("facet",))

    def _on_double_click(self, _event: tk.Event[tk.Misc]) -> None:
        item = self._tree.focus()
        if not item:
            return

        values = self._tree.item(item, "values")
        parent = self._tree.parent(item)
        field = self._tree.item(parent, "text")
        value = values[0] if values else ""
        if field and value:
            self._on_select(field, value)


class TourOverlay(tk.Toplevel):
    """Simple first-run tour overlay."""

    def __init__(
        self,
        master: tk.Misc,
        steps: Sequence[tuple[str, str]],
    ) -> None:
        super().__init__(master)
        self.withdraw()
        self.attributes("-topmost", True)  # type: ignore[call-arg]
        self.title("Quick Tour")
        self.geometry("600x360")
        self._steps = list(steps)
        self._index = 0
        self._label = ttk.Label(
            self,
            text="",
            wraplength=560,
            justify="left",
        )
        self._label.pack(padx=16, pady=16, fill="both", expand=True)
        self._button = ttk.Button(self, text="Next ▶", command=self._advance)
        self._button.pack(pady=8)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def start(self) -> None:
        self.deiconify()
        self._render()

    def _render(self) -> None:
        if not self._steps:
            self.destroy()
            return

        title, body = self._steps[self._index]
        self._label.configure(text=f"{title}\n\n{body}")

    def _advance(self) -> None:
        self._index += 1
        if self._index >= len(self._steps):
            self.destroy()
        else:
            self._render()


class TooltipLib:
    """Load tooltip copy from disk and attach it to widgets."""

    def __init__(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                self._data: dict[str, str] = json.load(handle)
        except Exception:  # pragma: no cover - defensive fallback
            self._data = {}

    def attach(self, widget: tk.Misc, key: str) -> None:
        tip = self._data.get(key)
        if tip:
            ToolTip(widget, tip, delay=100)
