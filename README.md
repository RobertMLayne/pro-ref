
# pro-ref mainline (drop-in)

This archive provides providers, themes, schemas, GUI, client, exporters, tests, and CI workflow configured for the USPTO ODP Patent File Wrapper API.

See `docs/README.md` for usage.

Pull requests run offline Windows regressions, including workflow and optional
MSI-signing checks. Main/nightly packaging and manual/main MSI builds retain
their existing artifact names. See `docs/README.md` for build prerequisites
and the distinction between workflow checks and installer acceptance.
