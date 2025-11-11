
# pro-ref — USPTO ODP PFW GUI (desktop)

**What you get:** dynamic, schema-driven GUI for USPTO Patent File Wrapper (PFW) with documents, bulk browser, a GET composer, preset manager, EndNote export, VCR test suite, and CI.

## Quick start
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m api_gui
```

### Record VCR cassettes (live)
```bash
export USPTO_ODP_API_KEY=...   # set your key
python scripts/record_cassettes.py
```

### EndNote
- Mapping: `src/api_gui/export/endnote_field_map.uspto_pfw.json`
- Custom Reference Type Table (EndNote 2025): `src/api_gui/export/EndNote_2025_for_Windows_Custom_Reference_Type_Table.xml`
- Exporter: `src/api_gui/export/endnote_export.py`

### Schemas
- PFW response: `src/api_gui/schemas/patent-data-schema.json`
- Bulk listing: `src/api_gui/schemas/bulkdata-response-schema.json`
- Petition decision: `src/api_gui/schemas/petition-decision-schema.json`

### CI
- GitHub Actions workflow builds and uploads nightly artifact, and (optionally) Windows installer via PyInstaller.

### Screenshots/GIFs
Commit them under `docs/images/`.
