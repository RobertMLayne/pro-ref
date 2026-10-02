
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

Pull requests run `python -m pytest -q` on Windows with `VCR_MODE=none` and
without USPTO service credentials. Tests with unavailable saved cassettes or
live API credentials remain explicit skips. The PR check does not create an
MSI, sign a release, or publish an installer.

Main/nightly EXE builds and manual/main MSI builds use the existing `run.py`
launcher with `--paths src --add-data "src/api_gui:api_gui"`; provider,
schema, theme, and export resources sit beside the frozen `api_gui` package.
The MSI build uses WiX v3's installed `WIX` root and its `bin/candle.exe` and
`bin/light.exe`, and refuses missing tools or failed compiler/linker commands.

Signing remains optional. `WINDOWS_CERT_PFX` (base64 PFX) and
`WINDOWS_CERT_PWD` enter only the signing step's environment. The helper
`scripts/sign_windows.ps1` skips absent certificates, passes values as data,
removes its temporary PFX on success or failure, and fails the job when signing
fails. Artifact names remain `api-gui-windows` and `pro-ref-msi`.

The added regressions exercise absent certificates and synthetic successful
and failing signers, preserve password quoting, parse PowerShell, and check
the launcher/resource/MSI contracts. They do not establish an actual
PyInstaller build, installed GUI launch, WiX compile, trusted signature, or
installation roundtrip. Those require Windows packaging tools and a real
manual/main build. Python dependencies and the Chocolatey WiX package remain
floating; full dependency locking is a separate follow-up.

### Screenshots/GIFs
Commit them under `docs/images/`.
