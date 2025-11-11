---
applyTo: "**/*.{ts,tsx}"
description: TypeScript coding standards
---

# TypeScript coding standards

- Use TS strict mode. No `any` unless documented with a comment explaining why.
- Prefer discriminated unions, `readonly` props, and immutability.
- React: function components with hooks; custom hooks for side-effects; no ambient globals.
- Tests with Vitest/Jest; one test file per module.
- Avoid mutable state; prefer functional updates and immutable data structures.
- Enums: use `as const` assertions and type inference instead where possible.
- Module organization: keep related types, interfaces, and implementations in the same file unless it exceeds ~300 lines.
