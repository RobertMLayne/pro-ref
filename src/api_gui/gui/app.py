
import json, os, tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import requests
import ttkbootstrap as tb
from ttkbootstrap.style import Style

from ..clients.uspto_odp import USPTOODPClient
from ..util.provider_loader import load_providers
from ..util.error_helper import suggest_url_encoding
from .widgets import FacetsPanel, PillBar, TourOverlay, TooltipLib
from ..util.presets import save_preset, load_preset, list_presets
from ..util import settings

APP_TITLE = "API GUI — USPTO PFW"
THEME_DEFAULT = "lumenci_light"

class App(tb.Window):
    def __init__(self):
        super().__init__(themename=THEME_DEFAULT)
        self.title(APP_TITLE)
        self.geometry("1200x800")
        self.providers = load_providers(os.path.join(os.path.dirname(__file__), "..", "providers"))
        self.cfg = settings.load_settings()
        self.tooltiplib = TooltipLib(os.path.join(os.path.dirname(__file__), "odp_dsl_examples.json"))
        self._build_menu()
        self._build_layout()
        self._first_run_tour()

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="Save Preset…", command=self._save_preset)
        filem.add_command(label="Load Preset…", command=self._load_preset)
        filem.add_separator()
        filem.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=filem)

        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label="ODP Guide", command=lambda: webbrowser.open("https://data.uspto.gov/apis/patent-file-wrapper/search"))
        menubar.add_cascade(label="Help", menu=helpm)

        settingsm = tk.Menu(menubar, tearoff=0)
        settingsm.add_command(label="Save Settings", command=self._save_settings)
        menubar.add_cascade(label="Settings", menu=settingsm)

    def _build_layout(self):
        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # left: provider/operation
        left = ttk.Frame(paned, padding=8)
        paned.add(left, weight=1)
        ttk.Label(left, text="Provider/Operation").pack(anchor="w")
        self.provider_cb = ttk.Combobox(left, values=sorted(self.providers.keys()))
        if self.provider_cb["values"]:
            self.provider_cb.current(0)
        self.provider_cb.pack(fill="x")
        ttk.Label(left, text="API Key (X-API-KEY)").pack(anchor="w", pady=(8,0))
        self.api_key_var = tk.StringVar(value=self.cfg.get('api_keys',{}).get('uspto_odp',''))
        ttk.Entry(left, textvariable=self.api_key_var, show="•").pack(fill="x")

        ttk.Separator(left).pack(fill="x", pady=8)
        ttk.Label(left, text="Presets").pack(anchor="w")
        self.presets_lb = tk.Listbox(left, height=6)
        self.presets_lb.pack(fill="both", expand=True)
        self._refresh_presets()

        # center: query tabs
        center = ttk.Notebook(paned)
        paned.add(center, weight=3)

        # Search (POST)
        self.post_tab = ttk.Frame(center, padding=8)
        center.add(self.post_tab, text="Search (POST)")
        self._build_post_tab(self.post_tab)

        # GET pane
        self.get_tab = ttk.Frame(center, padding=8)
        center.add(self.get_tab, text="GET Composer")
        self._build_get_tab(self.get_tab)

        # Documents
        self.docs_tab = ttk.Frame(center, padding=8)
        center.add(self.docs_tab, text="Documents")
        self._build_docs_tab(self.docs_tab)

        # Bulk
        self.bulk_tab = ttk.Frame(center, padding=8)
        center.add(self.bulk_tab, text="Bulk")
        self._build_bulk_tab(self.bulk_tab)

        # right: results
        right = ttk.Frame(paned, padding=8)
        paned.add(right, weight=2)
        ttk.Label(right, text="Results").pack(anchor="w")
        self.results = tk.Text(right, wrap="none")
        self.results.pack(fill="both", expand=True)
        self.facets_panel = FacetsPanel(right, on_select=self._apply_facet_filter)
        self.facets_panel.pack(fill="x")

        self.pill_bar = PillBar(right, on_remove=self._remove_filter_pill)
        self.pill_bar.pack(fill="x")

    # ------------- POST Search tab -------------
    def _build_post_tab(self, frame):
        self.q_var = tk.StringVar()
        ttk.Label(frame, text="q (Simple Query String or free-form)").grid(row=0, column=0, sticky="w")
        q_entry = ttk.Entry(frame, textvariable=self.q_var)
        q_entry.grid(row=0, column=1, sticky="ew", padx=4)
        self.tooltiplib.attach(q_entry, "dsl_field_search")
        frame.grid_columnconfigure(1, weight=1)

        self.filters = []
        ttk.Button(frame, text="Add Filter", command=lambda: self._add_filter_row(frame)).grid(row=1,column=0, pady=4, sticky="w")
        ttk.Button(frame, text="Search", command=self._do_post_search).grid(row=1, column=1, sticky="e", pady=4)

    def _add_filter_row(self, frame):
        row = len(self.filters) + 2
        name_var = tk.StringVar()
        val_var = tk.StringVar()
        n = ttk.Entry(frame, textvariable=name_var)
        v = ttk.Entry(frame, textvariable=val_var)
        n.grid(row=row, column=0, sticky="ew", padx=2, pady=2)
        v.grid(row=row, column=1, sticky="ew", padx=2, pady=2)
        self.filters.append((name_var, val_var))

    def _payload_from_ui(self):
        filters = [{"name": n.get(), "value": [v.get()]} for n,v in self.filters if n.get() and v.get()]
        payload = {"q": self.q_var.get() or None}
        if filters:
            payload["filters"] = filters
        payload["pagination"] = {"offset": 0, "limit": 25}
        # Request facets for common fields
        payload["facets"] = ["applicationMetaData.applicationTypeLabelName", "applicationMetaData.applicationStatusCode"]
        return payload

    def _client(self):
        key = self.api_key_var.get().strip()
        os.environ["USPTO_ODP_API_KEY"] = key
        return USPTOODPClient("https://api.uspto.gov", api_key_env="USPTO_ODP_API_KEY")

    def _do_post_search(self):
        try:
            cli = self._client()
            payload = self._payload_from_ui()
            data = cli.search_pfw(payload)
            self._render_results(data)
            self._update_facets(data.get("facets"))
            # Update pill bar
            active = []
            for f in payload.get("filters", []):
                for val in f.get("value", []):
                    active.append((f["name"], val))
            self.pill_bar.set_filters(active)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_facets(self, facets):
        if facets:
            self.facets_panel.set_facets(facets)

    def _apply_facet_filter(self, field, value):
        self.filters.append((tk.StringVar(value=field), tk.StringVar(value=value)))
        self._do_post_search()

    def _remove_filter_pill(self, name, val):
        self.filters = [(n,v) for (n,v) in self.filters if not (n.get()==name and v.get()==val)]
        self._do_post_search()

    # ------------- GET composer -------------
    def _build_get_tab(self, frame):
        ttk.Label(frame, text="q (GET)").grid(row=0, column=0, sticky="w")
        self.get_q_var = tk.StringVar()
        e = ttk.Entry(frame, textvariable=self.get_q_var)
        e.grid(row=0, column=1, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        self.tooltiplib.attach(e, "phrase")

        self.get_url_lbl = ttk.Label(frame, text="")
        self.get_url_lbl.grid(row=1, column=0, columnspan=2, sticky="w", pady=4)

        ttk.Button(frame, text="Preview URL", command=self._build_get_url).grid(row=2, column=0, sticky="w")
        ttk.Button(frame, text="Copy as cURL", command=self._copy_curl).grid(row=2, column=1, sticky="e")
        ttk.Button(frame, text="Open in browser", command=self._open_in_browser).grid(row=2, column=1, sticky="w", padx=(120,0))

        self.get_suggestions = tk.Text(frame, height=4)
        self.get_suggestions.grid(row=3, column=0, columnspan=2, sticky="ew")

    def _build_get_url(self):
        q = self.get_q_var.get().strip()
        base = "https://api.uspto.gov/api/v1/patent/applications/search"
        if q:
            from urllib.parse import quote
            url = f"{base}?q={quote(q, safe=':()*[]\"')}".replace('"', '%22')
        else:
            url = base
        self.get_url_lbl.configure(text=url)
        sugg = suggest_url_encoding(q)
        self.get_suggestions.delete("1.0", "end")
        self.get_suggestions.insert("end", "Encoding tips:\n" + "\n".join("- " + s for s in sugg))

    def _copy_curl(self):
        url = self.get_url_lbl.cget("text")
        key = self.api_key_var.get().strip()
        curl = f'curl -H "X-API-KEY: {key}" "{url}"'
        self.clipboard_clear()
        self.clipboard_append(curl)

    def _open_in_browser(self):
        url = self.get_url_lbl.cget("text")
        webbrowser.open(url)

    # ------------- Documents tab -------------
    def _build_docs_tab(self, frame):
        ttk.Label(frame, text="Application #").grid(row=0, column=0, sticky="w")
        self.doc_app_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.doc_app_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(frame, text="List Documents", command=self._list_docs).grid(row=0, column=2, padx=4)
        frame.grid_columnconfigure(1, weight=1)

        self.docs_tree = ttk.Treeview(frame, columns=("date","code","desc","pages","url"), show="headings", height=12)
        for c in ("date","code","desc","pages","url"):
            self.docs_tree.heading(c, text=c.title())
        self.docs_tree.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=6)
        frame.grid_rowconfigure(1, weight=1)

        ttk.Button(frame, text="Download PDF", command=self._download_selected_pdf).grid(row=2, column=2, sticky="e")

    def _list_docs(self):
        cli = self._client()
        app = self.doc_app_var.get().strip()
        data = cli.pfw_documents(app)
        self.docs_tree.delete(*self.docs_tree.get_children())
        for item in data.get("documentBag", []):
            date = item.get("officialDate","")
            code = item.get("documentCode","")
            desc = item.get("documentCodeDescriptionText","")
            pages = ""
            url = ""
            for opt in item.get("downloadOptionBag", []):
                if opt.get("mimeTypeIdentifier") in ("PDF","pdf"):
                    url = opt.get("downloadUrl") or opt.get("documentURI") or ""
                    pages = opt.get("pageTotalQuantity","")
            self.docs_tree.insert("", "end", values=(date, code, desc, str(pages), url))

    def _download_selected_pdf(self):
        sel = self.docs_tree.focus()
        if not sel:
            return
        vals = self.docs_tree.item(sel, "values")
        url = vals[4]
        app = self.doc_app_var.get().strip()
        if not url:
            messagebox.showwarning("No PDF", "No PDF URL available for this document.")
            return
        dest = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"{app}_{vals[1]}.pdf")
        if not dest:
            return
        # Direct download via requests
        cli = self._client()
        import requests
        with cli.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1024*512):
                    if chunk:
                        f.write(chunk)
        messagebox.showinfo("Saved", dest)

    # ------------- Bulk tab -------------
    def _build_bulk_tab(self, frame):
        ttk.Label(frame, text="Product").grid(row=0, column=0, sticky="w")
        self.bulk_prod_var = tk.StringVar(value="PTFWPRD")
        ttk.Combobox(frame, textvariable=self.bulk_prod_var, values=("PTFWPRD","PTFWPRE")).grid(row=0, column=1, sticky="w")
        ttk.Button(frame, text="List Files", command=self._bulk_list).grid(row=0, column=2, padx=4)
        self.bulk_tree = ttk.Treeview(frame, columns=("name","size","from","to","release","download"), show="headings", height=12)
        for c in ("name","size","from","to","release","download"):
            self.bulk_tree.heading(c, text=c.title())
        self.bulk_tree.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=6)
        frame.grid_rowconfigure(1, weight=1)
        ttk.Button(frame, text="Download Selected", command=self._bulk_download).grid(row=2, column=2, sticky="e")

    def _bulk_list(self):
        cli = self._client()
        pid = self.bulk_prod_var.get()
        data = cli.bulk_products(pid, latest=True)
        self.bulk_tree.delete(*self.bulk_tree.get_children())
        for p in data.get("bulkDataProductBag", []):
            for f in p.get("productFileBag", {}).get("fileDataBag", []):
                self.bulk_tree.insert("", "end", values=(f.get("fileName"), f.get("fileSize"),
                                                         f.get("fileDataFromDate"), f.get("fileDataToDate"),
                                                         f.get("fileReleaseDate"), f.get("fileDownloadURI")))

    def _bulk_download(self):
        sel = self.bulk_tree.focus()
        if not sel: return
        vals = self.bulk_tree.item(sel, "values")
        fname = vals[0]; url = vals[5]; pid = self.bulk_prod_var.get()
        dest = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=fname)
        if not dest: return
        cli = self._client()
        import requests
        with cli.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1024*1024):
                    if chunk: f.write(chunk)
        messagebox.showinfo("Saved", dest)

    # ------------- Presets -------------
    def _save_preset(self):
        payload = self._payload_from_ui()
        name = tk.simpledialog.askstring("Preset name", "Name:")
        if not name: return
        path = save_preset(name, payload)
        self._refresh_presets()
        messagebox.showinfo("Preset saved", path)

    def _load_preset(self):
        sel = self.presets_lb.curselection()
        if not sel: return
        name = self.presets_lb.get(sel[0])
        payload = load_preset(name)
        self.q_var.set(payload.get("q") or "")
        self.filters.clear()
        # Rebuild simple single-value filter UI
        for child in self.post_tab.grid_slaves():
            info = child.grid_info()
            if info["row"] >= 2:
                child.destroy()
        for f in (payload.get("filters") or []):
            self._add_filter_row(self.post_tab)
            self.filters[-1][0].set(f.get("name",""))
            self.filters[-1][1].set(", ".join(f.get("value", [])))

    def _refresh_presets(self):
        self.presets_lb.delete(0, "end")
        for name in list_presets():
            self.presets_lb.insert("end", name)

    # ------------- First-run tour -------------
    def _first_run_tour(self):
        if not os.path.exists(os.path.expanduser("~/.api-gui/.tour_done")):
            steps = [
                ("Welcome", "This 90-second tour will show you how to run your first search."),
                ("Enter API Key", "Paste your USPTO ODP API key in the left pane."),
                ("Search", "Type a query or use filters, then click Search. Facets appear with counts. Double-click a bucket to filter."),
                ("GET Composer", "Switch to GET Composer to build URL-encoded queries. Use 'Copy as cURL' to share."),
                ("Documents & Bulk", "Use the Documents tab to list and download PDFs; Bulk to browse weekly/daily datasets."),
            ]
            tour = TourOverlay(self, steps)
            tour.start()
            os.makedirs(os.path.expanduser("~/.api-gui"), exist_ok=True)
            open(os.path.expanduser("~/.api-gui/.tour_done"), "w").close()



    def _save_settings(self):
        self.cfg['api_keys']['uspto_odp'] = self.api_key_var.get().strip()
        settings.save_settings(self.cfg)
        messagebox.showinfo("Settings", "Saved.")


def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
