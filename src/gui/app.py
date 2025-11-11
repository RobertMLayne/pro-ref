
import json, os, threading
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List

from ..core.provider_loader import ProviderRegistry
from ..clients.uspto import USPTOClient
from ..utils.encoding_helper import encode_query_part, suggest_encoding_issue
from ..utils.schema_validator import validate_json

APP_DIR = os.path.join(os.path.expanduser('~'), '.pro-ref')
PRESETS_DIR = os.path.join(APP_DIR, 'presets')
os.makedirs(PRESETS_DIR, exist_ok=True)

class App(tb.Window):
    def __init__(self):
        super().__init__(themename='litera')  # fallback; user can load custom themes
        self.title('Pro-Ref — Multi-API GUI')
        self.geometry('1200x800')

        # top toolbar
        top = ttk.Frame(self)
        top.pack(side=TOP, fill=X)
        ttk.Label(top, text='Provider').pack(side=LEFT, padx=4)
        self.provider_cb = ttk.Combobox(top, state='readonly', width=40)
        self.provider_cb.pack(side=LEFT, padx=4)
        ttk.Button(top, text='Settings', command=self.open_settings).pack(side=LEFT, padx=4)
        ttk.Button(top, text='First-run tour', command=self.show_tour).pack(side=LEFT, padx=4)
        ttk.Button(top, text='Save Preset', command=self.save_preset).pack(side=LEFT, padx=4)
        ttk.Button(top, text='Load Preset', command=self.load_preset).pack(side=LEFT, padx=4)

        # main panes
        main = ttk.PanedWindow(self, orient=HORIZONTAL)
        main.pack(side=TOP, fill=BOTH, expand=YES)

        # left: operations + examples
        left = ttk.Notebook(main, width=300)
        self.ops_frame = ttk.Frame(left)
        left.add(self.ops_frame, text='Operation')
        self.examples_frame = ttk.Frame(left)
        left.add(self.examples_frame, text='DSL Examples')
        main.add(left, weight=1)

        # center: parameters
        self.form_nb = ttk.Notebook(main)
        self.form_tab = ttk.Frame(self.form_nb)
        self.form_nb.add(self.form_tab, text='POST')
        self.get_tab = ttk.Frame(self.form_nb)
        self.form_nb.add(self.get_tab, text='GET')
        main.add(self.form_nb, weight=3)

        # right: results
        right = ttk.Notebook(main)
        self.results_tab = ttk.Frame(right)
        right.add(self.results_tab, text='Results')
        self.json_tab = ttk.Frame(right)
        right.add(self.json_tab, text='JSON')
        main.add(right, weight=3)

        # results area
        self.results_tree = ttk.Treeview(self.results_tab, columns=('app','title','status'), show='headings')
        for c in ('app','title','status'):
            self.results_tree.heading(c, text=c)
        self.results_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.facets_list = ttk.Treeview(self.results_tab, columns=('count',), show='tree headings', height=20)
        self.facets_list.heading('#0', text='Facet')
        self.facets_list.heading('count', text='Count')
        self.facets_list.pack(side=RIGHT, fill=Y)
        self.facets_list.bind('<<TreeviewSelect>>', self.on_facet_click)

        # json area
        self.json_text = ttk.Text(self.json_tab, wrap='none')
        self.json_text.pack(fill=BOTH, expand=YES)

        # provider registry
        self.registry = ProviderRegistry(os.path.join(os.path.dirname(__file__), '..', 'providers'))
        self.registry.load_all()
        self.provider_cb['values'] = self.registry.list()
        if self.provider_cb['values']:
            self.provider_cb.current(0)
        self.provider_cb.bind('<<ComboboxSelected>>', lambda e: self.load_provider())
        self.load_provider()

    def load_provider(self):
        pid = self.provider_cb.get()
        meta = self.registry.get(pid)
        # build simple form for PFW search POST
        for w in self.form_tab.winfo_children():
            w.destroy()
        ttk.Label(self.form_tab, text='q').grid(row=0, column=0, sticky=W, padx=4, pady=2)
        self.q_entry = ttk.Entry(self.form_tab, width=80)
        self.q_entry.grid(row=0, column=1, sticky=EW, padx=4, pady=2)
        self.form_tab.grid_columnconfigure(1, weight=1)
        self.filters: List[Dict[str, Any]] = []
        ttk.Button(self.form_tab, text='Add Filter', command=self.add_filter_row).grid(row=1, column=0, padx=4)
        ttk.Button(self.form_tab, text='Run', command=self.run_post).grid(row=1, column=1, sticky=E, padx=4)

        # GET tab composer
        for w in self.get_tab.winfo_children():
            w.destroy()
        self.get_q = ttk.Entry(self.get_tab, width=60)
        self.get_filters = ttk.Entry(self.get_tab, width=60)
        self.get_range = ttk.Entry(self.get_tab, width=40)
        ttk.Label(self.get_tab, text='q (DSL)').grid(row=0, column=0, sticky=W, padx=4, pady=2)
        self.get_q.grid(row=0, column=1, sticky=EW, padx=4, pady=2)
        ttk.Label(self.get_tab, text='filters (field value, comma separated)').grid(row=1, column=0, sticky=W, padx=4, pady=2)
        self.get_filters.grid(row=1, column=1, sticky=EW, padx=4, pady=2)
        ttk.Label(self.get_tab, text='rangeFilters (field from:to)').grid(row=2, column=0, sticky=W, padx=4, pady=2)
        self.get_range.grid(row=2, column=1, sticky=EW, padx=4, pady=2)
        self.url_preview = ttk.Entry(self.get_tab, width=100)
        ttk.Button(self.get_tab, text='Preview URL', command=self.preview_get).grid(row=3, column=0, padx=4, pady=2)
        self.url_preview.grid(row=3, column=1, sticky=EW, padx=4, pady=2)
        ttk.Button(self.get_tab, text='GET & Retry', command=self.run_get).grid(row=4, column=1, sticky=E, padx=4, pady=2)

        # Examples per ODP guide
        for w in self.examples_frame.winfo_children():
            w.destroy()
        examples = [
            'applicationMetaData.applicationTypeLabelName:Utility',
            '"Patented Case"',
            'applicationMetaData.filingDate:[2024-01-01 TO 2024-08-30]',
            'applicationMetaData.firstApplicantName:Technolog*',
        ]
        ttk.Label(self.examples_frame, text='ODP DSL Examples').pack(anchor=W, padx=4, pady=4)
        for ex in examples:
            b = ttk.Button(self.examples_frame, text=ex, command=lambda e=ex: self.q_entry.insert(0, e))
            b.pack(anchor=W, padx=4, pady=2)

    def add_filter_row(self):
        idx = len(self.filters)
        f = {'name': ttk.Entry(self.form_tab, width=60), 'value': ttk.Entry(self.form_tab, width=40)}
        f['name'].grid(row=2+idx, column=0, sticky=EW, padx=4, pady=2)
        f['value'].grid(row=2+idx, column=1, sticky=EW, padx=4, pady=2)
        self.filters.append(f)

    def run_post(self):
        payload = {'q': self.q_entry.get() or None, 'filters': [], 'pagination': {'offset': 0, 'limit': 25}, 'facets': ['applicationMetaData.applicationTypeLabelName','applicationMetaData.applicationStatusCode']}
        for f in self.filters:
            name = f['name'].get().strip()
            value = f['value'].get().strip()
            if name and value:
                payload['filters'].append({'name': name, 'value': [v.strip() for v in value.split(',')]})
        threading.Thread(target=self._do_post, args=(payload,), daemon=True).start()

    def _do_post(self, payload):
        try:
            client = USPTOClient()
            data = client.pfw_search(payload)
            self.render_results(data)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def preview_get(self):
        base = 'https://api.uspto.gov/api/v1/patent/applications/search'
        params = []
        if self.get_q.get().strip():
            params.append('q=' + encode_query_part(self.get_q.get().strip()))
        if self.get_filters.get().strip():
            pairs = [p.strip() for p in self.get_filters.get().split(',') if p.strip()]
            for p in pairs:
                params.append('filters=' + encode_query_part(p))
        if self.get_range.get().strip():
            params.append('rangeFilters=' + encode_query_part(self.get_range.get().strip()))
        url = base + ('?' + '&'.join(params) if params else '')
        self.url_preview.delete(0, 'end')
        self.url_preview.insert(0, url)
        tip = suggest_encoding_issue(url)
        if tip and 'No obvious' not in tip:
            messagebox.showinfo('Encoding tips', tip)

    def run_get(self):
        url = self.url_preview.get().strip()
        if not url:
            self.preview_get()
            url = self.url_preview.get().strip()
        # Convert back to params dict for client (since it applies API key etc.)
        from urllib.parse import urlparse, parse_qsl
        q = urlparse(url)
        params = dict(parse_qsl(q.query))
        threading.Thread(target=self._do_get, args=(params,), daemon=True).start()

    def _do_get(self, params):
        try:
            client = USPTOClient()
            data = client.pfw_search_get(params)
            self.render_results(data)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def render_results(self, data: Dict[str, Any]):
        # JSON view
        import json as _json
        self.json_text.delete('1.0', 'end')
        self.json_text.insert('1.0', _json.dumps(data, indent=2))

        # table
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)
        bag = data.get('patentFileWrapperDataBag') or data.get('petitionDecisionDataBag') or []
        for row in bag:
            app = row.get('applicationNumberText', '—')
            title = (row.get('applicationMetaData') or {}).get('inventionTitle') or row.get('inventionTitle') or '—'
            status = (row.get('applicationMetaData') or {}).get('applicationStatusDescriptionText') or ''
            self.results_tree.insert('', 'end', values=(app, title, status))

        # facets to panel (if present), and requery on click
        for i in self.facets_list.get_children():
            self.facets_list.delete(i)
        facets = data.get('facets') or {}
        for fname, items in facets.items():
            parent = self.facets_list.insert('', 'end', text=fname, values=('—',))
            for it in items:
                self.facets_list.insert(parent, 'end', text=str(it.get('value')), values=(it.get('count')))

    def on_facet_click(self, event=None):
        sel = self.facets_list.selection()
        if not sel:
            return
        item = self.facets_list.item(sel[0])
        parent = self.facets_list.parent(sel[0])
        if not parent:
            return
        facet_name = self.facets_list.item(parent)['text']
        facet_value = item['text']
        # push into filters and requery
        self.q_entry.delete(0, 'end')
        self.filters.clear()
        for w in self.form_tab.grid_slaves():
            info = w.grid_info()
            if info['row'] >= 2:
                w.destroy()
        self.add_filter_row()
        self.filters[0]['name'].insert(0, facet_name)
        self.filters[0]['value'].insert(0, facet_value)
        self.run_post()

    def open_settings(self):
        top = tb.Toplevel(self)
        top.title('Settings')
        k = ttk.Entry(top, width=60)
        k.insert(0, os.getenv('USPTO_ODP_API_KEY',''))
        ttk.Label(top, text='USPTO ODP API KEY').pack(anchor=W, padx=6, pady=4)
        k.pack(fill=X, padx=6)
        def save():
            # store in user env file
            path = os.path.join(APP_DIR, 'env.txt')
            with open(path,'w',encoding='utf-8') as f:
                f.write('USPTO_ODP_API_KEY=' + k.get().strip())
            messagebox.showinfo('Saved', f'Wrote {path}. Restart app to load.')
            top.destroy()
        ttk.Button(top, text='Save', command=save).pack(pady=6)

    def show_tour(self):
        messagebox.showinfo('Tour', 'Welcome! 1) Select provider. 2) Type a query or add filters. 3) Run. Click a facet to refine. Use GET tab to compose URL with encoding helper.')

    def save_preset(self):
        payload = {'q': self.q_entry.get(), 'filters': []}
        for f in self.filters:
            name, value = f['name'].get(), f['value'].get()
            if name and value:
                payload['filters'].append({'name': name, 'value': [v.strip() for v in value.split(',')]})
        path = filedialog.asksaveasfilename(defaultextension='.json', initialdir=PRESETS_DIR)
        if path:
            with open(path,'w',encoding='utf-8') as f:
                json.dump(payload, f, indent=2)

    def load_preset(self):
        path = filedialog.askopenfilename(defaultextension='.json', initialdir=PRESETS_DIR)
        if not path:
            return
        with open(path,'r',encoding='utf-8') as f:
            p = json.load(f)
        self.q_entry.delete(0,'end')
        self.q_entry.insert(0, p.get('q',''))
        # reset filters
        self.filters.clear()
        for w in self.form_tab.grid_slaves():
            info = w.grid_info()
            if info['row'] >= 2:
                w.destroy()
        for flt in p.get('filters',[]):
            self.add_filter_row()
            self.filters[-1]['name'].insert(0, flt.get('name',''))
            self.filters[-1]['value'].insert(0, ', '.join(flt.get('value',[])))

def main():
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()
