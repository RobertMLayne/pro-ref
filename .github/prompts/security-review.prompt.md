---
description: Security review of changed files
mode: ask
---

Review the diff in #changes and report:
- input validation, authZ/authN, secret handling, injection, SSRF, deserialization, path traversal
- dependency and supply-chain risks

Return a table: Issue | Severity | Evidence | Fix.
