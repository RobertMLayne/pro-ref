---
description: Plan and implement a feature with tests first
mode: agent
tools: ["search", "codebase", "problems"]
---

You will propose a plan, write failing tests, implement the feature, and update docs.

Workflow:
1) Plan: list impacted modules, risks, acceptance criteria.
2) Tests first: create failing tests under `/tests` that reflect the plan.
3) Implementation: minimal changes to pass tests.
4) Docs: update README and `/docs`.
5) Output: patch diff, new files, and a short migration note.
