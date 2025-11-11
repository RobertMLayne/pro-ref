# Agent operating rules

- Obey repository instructions and instruction files. Never bypass tests or security checks.
- Prefer behavior‑preserving changes. For non‑trivial edits: plan → tests → minimal change → doc update.
- Always propose unit tests before edits and run them after edits.
- Follow project layout: `/src /tests /docs /ci`. Keep READMEs and changelogs updated.
- Prefer reproducible envs and lockfiles. Do not add global installs.
- Respect `.gitignore` and lint/format configs already present.
- Produce diffs and commands in shell‑agnostic form. Avoid destructive commands unless explicitly approved.

## Security

- Never introduce secrets. Use env vars and secret stores. Do not fetch untrusted code.
- Use parameterized queries, input validation, and safe file I/O. Prefer constant‑time comparisons for secrets.

## When unsure

- Ask for constraints, then proceed with smallest reversible step.
