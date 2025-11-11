---
applyTo: "**/*.rs"
description: Rust coding standards
---

# Rust coding standards

- Keep code `clippy` clean. Run `cargo clippy -- -D warnings` before committing.
- Prefer `?` error propagation and `thiserror` for custom error types.
- Avoid `unsafe` unless justified and isolated. Add a safety section in comments explaining invariants.
- Benchmarks under `benches/` using `criterion` for non-trivial performance-sensitive code.
- Use `cargo fmt` with default style. Run `cargo test` before pushing.
- Prefer owned types; use references only where ownership transfer would be inefficient or semantically wrong.
- Documentation: include doc comments on public items; provide examples in doc tests where practical.
