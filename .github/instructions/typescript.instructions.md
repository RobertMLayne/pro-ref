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

## JSON Schema dialect for tool definitions

When generating JSON Schema from Zod for MCP tool parameters:

- **Default**: Emit `draft-7` schema (compatible with current VS Code JSON validator).
  - VS Code's JSON validator does not yet support `draft-2020-12` features like `$dynamicRef`. See VS Code's open issues for JSON schema support.
  - Waiting for VS Code to upgrade blocks developers; server-side dialect switching is the highest-leverage fix.
- **Configuration**: Add a `FIRECRAWL_JSON_SCHEMA_DIALECT` environment variable to Firecrawl and other MCP tool providers.
  - Default: `"draft-7"`
  - Accepted values: `"draft-7"`, `"draft-2020-12"`, `"draft-4"`, `"openapi-3.0"` (per Zod v4 docs).
- **Implementation** (Zod v4):
  ```typescript
  import * as z from "zod";

  const DIALECT = process.env.FIRECRAWL_JSON_SCHEMA_DIALECT ?? "draft-7";

  const ScrapeArgs = z.object({
    url: z.string().url(),
    // ...rest of args...
  });

  // Emit JSON Schema for the tool parameters
  const inputSchema = z.toJSONSchema(ScrapeArgs, { target: DIALECT });
  // Optional: delete inputSchema.$schema if you don't want to expose a meta-schema
  ```
- **Why this approach**: This is behavior-preserving (draft-7 does not reduce tool fidelity), immediate (no wait for VS Code upgrades), and allows power users to opt in to draft-2020-12 when their tooling is ready.
