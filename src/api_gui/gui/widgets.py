
import json, tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from ttkbootstrap.tooltip import ToolTip

class PillBar(ttk.Frame):
    def __init__(self, master, on_remove):
        super().__init__(master)
        self.on_remove = on_remove
        self.pills = []

    def set_filters(self, filters: list[tuple[str,str]]):
        for w in self.winfo_children():
            w.destroy()
        self.pills.clear()
        for name, val in filters:
            pill = ttk.Button(self, text=f"{name}: {val} ✕", command=lambda n=name,v=val: self.on_remove(n, v))
            pill.pack(side="left", padx=2, pady=2)

class FacetsPanel(ttk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master)
        self.on_select = on_select
        self.tree = ttk.Treeview(self, columns=("value","count"), show="tree headings", height=10)
        self.tree.heading("#0", text="Field")
        self.tree.heading("value", text="Value")
        self.tree.heading("count", text="Count")
        self.tree.pack(fill="both", expand=True)

    def set_facets(self, facets: dict):
        self.tree.delete(*self.tree.get_children())
        for field, buckets in (facets or {}).items():
            parent = self.tree.insert("", "end", text=field, open=True)
            for b in buckets:
                val = b.get("value")
                cnt = b.get("count")
                nid = self.tree.insert(parent, "end", text="", values=(val, cnt))
                self.tree.item(nid, tags=("facet",))
        self.tree.tag_bind("facet", "<Double-1>", self._on_dbl)

    def _on_dbl(self, event):
        item = self.tree.focus()
        vals = self.tree.item(item, "values")
        parent = self.tree.parent(item)
        field = self.tree.item(parent, "text")
        val = vals[0]
        self.on_select(field, val)

class TourOverlay(tk.Toplevel):
    def __init__(self, master, steps: list[tuple[str,str]]):
        super().__init__(master)
        self.withdraw()
        self.attributes("-topmost", True)
        self.title("Quick Tour")
        self.geometry("600x360")
        self.steps = steps
        self.idx = 0
        self.label = ttk.Label(self, text="", wraplength=560, justify="left")
        self.label.pack(padx=16, pady=16, fill="both", expand=True)
        self.btn = ttk.Button(self, text="Next ▶", command=self._next)
        self.btn.pack(pady=8)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def start(self):
        self.deiconify()
        self._render()

    def _render(self):
        title, body = self.steps[self.idx]
        self.label.configure(text=f"{title}\n\n{body}")

    def _next(self):
        self.idx += 1
        if self.idx >= len(self.steps):
            self.destroy()
        else:
            self._render()

class TooltipLib:
    def __init__(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}

    def attach(self, widget, key: str):
        tip = self.data.get(key)
        if tip:
            ToolTip(widget, tip, delay=100)
