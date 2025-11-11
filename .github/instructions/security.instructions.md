---
applyTo: "**"
description: Security baseline
---

# Security baseline

- No secrets in code. Use environment variables and `.env` files (excluded from VCS via `.gitignore`).
- Validate all inputs: check type, range, length, and format. Use allowlists where practical.
- Use parameterized queries for database access (no string concatenation).
- Escape output appropriately: HTML-escape in web contexts, shell-escape if needed.
- For web apps: implement CSRF protection, content security policy headers, and secure cookie flags (HttpOnly, Secure, SameSite).
- Log sensitive events (auth, access control, data changes) and avoid logging secrets, passwords, or API keys.
- Dependency management: regularly audit `pip`, `npm`, or `cargo` for known vulnerabilities.
- File I/O: use absolute paths or paths relative to known roots; avoid path traversal; validate file permissions.
