# Sparse Checkout Configuration

This repository uses Git sparse-checkout to include only the project files needed for development.

## Current patterns

```
.github/
AGENTS.md
README.md
pyproject.toml
run.py
```

## About sparse-checkout

Sparse-checkout allows selective file inclusion in the working tree, reducing unnecessary files and improving performance. The actual configuration is stored in `.git/info/sparse-checkout` (not tracked in Git).

To modify the patterns, use:

```bash
git sparse-checkout set --skip-checks <pattern1> <pattern2> ...
git sparse-checkout list          # View current patterns
git sparse-checkout revert        # Restore full working tree
```

## Rationale

The pro-ref project includes:
- `.github/` — Instruction files, prompts, chat modes, and toolsets for AI-assisted development
- `AGENTS.md` — Global agent operating rules
- `README.md` — Project documentation
- `pyproject.toml` — Python project configuration
- `run.py` — Main entry point for the application
- `src/` — Python source code (included implicitly when patterns are set)
- `tests/` — Test suite (included implicitly)
- `docs/` — Documentation (included implicitly)
- `scripts/` — Utility scripts (included implicitly)
