---
description: Generate unit tests for a file or selection
mode: agent
tools: ["codebase", "search", "problems"]
---

Given the selected code (`${selectedText}`), generate tests that:
- cover success, failure, and edge cases
- use deterministic data and assert specific outcomes
- avoid mocking unnecessary internals

Return the test file path and diff.
