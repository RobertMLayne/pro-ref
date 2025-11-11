<!--
This file is authored for AI coding assistants to help them be productive in this repository.
Keep it short, concrete and focused on discoverable, repo-specific patterns.
-->

# Copilot instructions for this repository

Purpose
- Short orientation to the projects' architecture, developer workflows, and code patterns so an automated assistant can make useful, low-risk changes.

Big picture (where to look)
- Entry / UI: `run.py` and `src/gui/app.py` (desktop GUI built with tkinter/ttk via `ttkbootstrap`).
- Providers & configuration: `src/providers/*.json` — these JSON files describe provider endpoints and field mappings.
- Client code: `src/clients/*` (the USPTO client(s) that call remote APIs).
- Core loader: `src/core/provider_loader.py` (loads provider JSON into runtime provider objects).
- Exporters: `src/exporters/` (EndNote mapping lives in `endnote_field_map.uspto_pfw.json` and exporter code in `endnote.py`).
- Utilities: `src/utils/` (http helpers, schema validation, download manager).
- Tests: `tests/` (integration tests use network-recording tools — see `vcrpy` in pyproject.toml).

Data flow / common patterns
- GUI -> provider_loader -> client -> utils.http -> response -> utils.schema_validator -> exporters.  Follow this path when adding features that touch request/response shapes.
- Provider behavior is driven by the `src/providers/*.json` files; prefer changing provider JSON when the change is only configuration.

Developer workflows (concrete commands)
- Run the app locally: `python run.py` (this starts the GUI using `src/gui/app.py`).
- Run tests: `python -m pytest -q` or `pytest -q tests/test_uspto_integration.py`.
- Build a standalone app (PyInstaller): `python -m PyInstaller --onefile src/gui/app.py` (pyproject.toml also names `src/gui/app.py` as the script).
- Formatting and linting: codebase prefers Python style: Black with line-length 79 and Flake8 for linting (see repo `.github` instructions). If a different linter (e.g. `ruff`) is present in CI tasks, follow the CI config.

Tests and network recordings
- Tests may use `vcrpy` to record HTTP interactions; when modifying client code, run tests and update/record cassettes carefully.
- Integration tests that hit the USPTO API may require API keys or environment variables — do not hardcode credentials. Use local env vars and keep secrets out of commits.

Conventions and constraints
- Language: Python 3.13, use type hints where practical.
- Commit message convention: `<area>: <imperative>` (short title) and a brief body describing rationale and risk.
- Keep changes minimal and file-scoped; when altering provider behavior, prefer adding a new provider JSON rather than wide code edits.

Integration points / examples
- Add or modify providers by editing or adding `src/providers/provider.*.json`. Provider loader expects a JSON shape — examine existing files like `provider.uspto.pfw.search.json` for examples.
- EndNote exporter mapping is in `src/exporters/endnote_field_map.uspto_pfw.json`; changes here affect output formatting.

Examples
- Sample provider JSON (minimal — place under `src/providers/` and follow existing file shapes):
```json
{
  "id": "uspto-pfw",
  "name": "USPTO PFW",
  "endpoint": "https://developer.uspto.gov/odps/api/v1/patents",
  "method": "GET",
  "params": {
    "q": "{query}",
    "rows": 25
  },
  "mappings": {
    "title": "invention_title",
    "authors": "inventors"
  }
}
```

- Running tests (example with env vars and vcrpy):
```powershell
# set API key and run a single integration test that uses vcrpy cassettes
$env:USPTO_API_KEY = 'REPLACE_ME'
$env:VCR_MODE = 'once'    # vcrpy mode: once, none, all, new_episodes
pytest -q tests/test_uspto_integration.py::test_search_flow -k search_flow
```

- Cassettes and where to update them: tests that use `vcrpy` typically create cassettes under `tests/fixtures/cassettes/` or next to tests; run tests locally to regenerate if API surface changed.
- Example EndNote mapping: `src/exporters/endnote_field_map.uspto_pfw.json` — edit the mapping keys there; `src/exporters/endnote.py` turns provider fields into EndNote fields.

Safety and review notes
- When changing commit history, avoid rewriting published history unless instructed by the repository owner. For test data / cassettes, prefer adding new recordings rather than modifying old ones.
- Avoid introducing network calls in unit tests; use `vcrpy` or mocking helpers in `src/utils`.

If anything is unclear or you need a specific example expanded (provider JSON fields, client auth flow, or test cassette locations), tell me which area and I'll update this file.
