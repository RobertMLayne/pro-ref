
# Pro-Ref (USPTO ODP — PFW)

Dynamic, schema-driven GUI for USPTO Open Data Portal (PFW) with descriptors for Search, Lookup, Documents, Bulk, and Petition Decisions. 
- **Facets panel**: click to push filters and auto re-query.
- **GET composer**: build query URLs with encoding tips; retry with one click.
- **Presets**: save/load POST payloads.
- **Download manager**: resumable downloads for bulk files.
- **EndNote Exporter**: RIS with attorneys/correspondence mapping; companion EndNote 2025 table in `docs/endnote/`.
- **TTKBootstrap themes**: Lumenci light/dark/high-contrast.

## Quickstart
```bash
python -m pip install -e .
set USPTO_ODP_API_KEY=...   # or use Settings dialog
python run.py
```

## Recording VCR cassettes
Set env `USPTO_ODP_API_KEY` and `RECORD_VCR=1` then run:
```bash
pytest -q
```
Cassettes will be created under `tests/cassettes/` and committed.

## Schemas & Validation
Tests assert responses against JSON Schemas in `docs/schemas/`.

## Packaging
- GitHub Action `windows-installer` builds a signed MSI (if secrets provided).
- CI uploads zip artifacts from main branch.

## Screenshots/GIFs
Put captures under `/docs/images`. (Optional script: `scripts/capture.py` can be added to automate.)

