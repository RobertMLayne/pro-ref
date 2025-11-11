---
description: Behavior‑preserving refactor guarded by tests
mode: agent
tools: ["codebase", "search", "problems"]
---

Goal: improve structure without changing behavior.

Steps:
- Identify seams and define invariants.
- Add or strengthen tests to lock behavior.
- Apply small refactors (rename, extract, inline, decompose).
- Keep coverage at or above baseline. Provide diff and rationale.
