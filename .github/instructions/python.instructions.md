---
applyTo: "**/*.py"
description: Python coding standards
---

# Python coding standards

- Target Python 3.13. Use `typing` and `typing_extensions` as needed.
- Always add type hints and `from __future__ import annotations` if not default.
- Format with Black (79 columns). Keep imports sorted but do not re-order for side-effects.
- Use pytest. Put tests under `/tests`, mirror module paths, one behavioral test per public function.
- Avoid mutable defaults. Prefer dataclasses or pydantic models for structured data.
- Use `pathlib.Path` and `subprocess.run(..., check=True)` not `os.system`.
- Docstrings: use triple-quoted strings; include Args, Returns, Raises sections for public functions.
- Error handling: prefer custom exceptions (inherit from Exception) for domain-specific errors; use `try/except` for expected failures, not flow control.
