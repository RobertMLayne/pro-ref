<!-- markdownlint-disable MD041 -->

# JSON Schema Dialect Configuration

This directory contains the implementation of configurable JSON Schema dialect support for MCP (Model Context Protocol) tool parameters.

## Overview

The schema dialect configuration module resolves VS Code JSON validator compatibility issues by:

1. **Defaulting to `draft-7`** — Compatible with current VS Code JSON validators
2. **Allowing opt-in to newer dialects** — Power users can upgrade via environment variable
3. **Supporting multiple dialects** — draft-7, draft-2020-12, draft-4, openapi-3.0
4. **Eliminating validator warnings** — Removes "MCP server has tools with invalid parameters" errors

## Why This Matters

VS Code's JSON schema validator does not yet support `draft-2020-12` features like `$dynamicRef`. Waiting for the editor upgrade blocks developers. This implementation uses server-side dialect switching to:

- ✅ Resolve VS Code validator errors immediately
- ✅ Maintain full tool fidelity (draft-7 supports current schemas)
- ✅ Enable future upgrades when VS Code support arrives
- ✅ Respect developer choice via environment configuration

## Files

### Core Implementation

- **`schema_dialect.py`** — Main module with dialect configuration and helper functions
  - `get_schema_dialect()` — Retrieve current dialect from environment
  - `add_schema_dialect()` — Add dialect metadata to schema dict
  - `ToolParameterSchema` — Helper class for MCP tool parameter schemas

### Examples & Tests

- **`schema_dialect_examples.py`** — Runnable examples showing usage patterns
  - Scrape tool example
  - Search tool example
  - Environment variable override demonstration

- **`test_schema_dialect.py`** — Comprehensive test suite (8 tests, all passing)
  - Dialect detection tests
  - Environment variable override tests
  - Schema generation tests
  - Edge case handling

## Usage

### Basic Usage

```python
from src.utils.schema_dialect import ToolParameterSchema

# Create a tool parameter schema
input_schema = ToolParameterSchema.from_dict(
    properties={
        "url": {
            "type": "string",
            "format": "uri",
            "description": "The URL to scrape",
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds",
        },
    },
    required=["url"],
    description="Input parameters for web scraping",
)

# Register the tool with MCP
tool = {
    "name": "scrape_page",
    "description": "Scrape a web page",
    "inputSchema": input_schema,
}
```

### Environment Configuration

```bash
# Use default draft-7 (recommended for VS Code)
python your_mcp_tool.py

# Opt in to draft-2020-12 for newer tooling
export FIRECRAWL_JSON_SCHEMA_DIALECT=draft-2020-12
python your_mcp_tool.py

# Other supported dialects
export FIRECRAWL_JSON_SCHEMA_DIALECT=draft-4
export FIRECRAWL_JSON_SCHEMA_DIALECT=openapi-3.0
```

## Configuration

The module reads the `FIRECRAWL_JSON_SCHEMA_DIALECT` environment variable:

| Value | Usage | VS Code Support |
|-------|-------|---|
| `draft-7` | **Default**. Recommended for current VS Code. | ✅ Full support |
| `draft-2020-12` | Latest standard. Requires VS Code 1.95+ (with workarounds). | ⚠️ Partial support |
| `draft-4` | Legacy support. | ✅ Full support |
| `openapi-3.0` | OpenAPI format. | ✅ Full support |

## Running Tests

```bash
# Run all tests
pytest tests/test_schema_dialect.py -v

# Or using uv
uvx pytest tests/test_schema_dialect.py -v
```

Output:
```
tests/test_schema_dialect.py::test_get_schema_dialect_default PASSED     [ 12%]
tests/test_schema_dialect.py::test_get_schema_dialect_from_env PASSED    [ 25%]
tests/test_schema_dialect.py::test_get_schema_dialect_invalid PASSED     [ 37%]
tests/test_schema_dialect.py::test_add_schema_dialect_draft7 PASSED      [ 50%]
tests/test_schema_dialect.py::test_add_schema_dialect_draft2020 PASSED   [ 62%]
tests/test_schema_dialect.py::test_tool_parameter_schema_create PASSED   [ 75%]
tests/test_schema_dialect.py::test_tool_parameter_schema_from_dict PASSED [ 87%]
tests/test_schema_dialect.py::test_tool_parameter_schema_without_required PASSED [100%]

8 passed in 0.02s
```

## Running Examples

```bash
# Display current dialect and example schemas
python src/utils/schema_dialect_examples.py

# Or with custom dialect
FIRECRAWL_JSON_SCHEMA_DIALECT=draft-2020-12 python src/utils/schema_dialect_examples.py
```

## Implementation Details

### Draft-7 (Default)

```python
# Emits clean schema without meta-schema declaration
# VS Code validator accepts it immediately
{
    "type": "object",
    "properties": {...},
    "required": [...]
}
```

### Draft-2020-12 and Higher

```python
# Includes $schema field for explicit dialect declaration
# Requires VS Code 1.95+ or explicit validator configuration
{
    "$schema": "https://json-schema.org/draft-2020-12/schema#",
    "type": "object",
    "properties": {...},
    "required": [...]
}
```

## Future Work

When VS Code's JSON validator adds native support for `draft-2020-12`:

1. Update documentation to recommend `draft-2020-12`
2. Consider changing default to newer dialect
3. Remove `$schema` field omission workaround for draft-7

Track VS Code JSON schema support:
- microsoft/vscode#251315 — General draft-2020-12 support
- microsoft/vscode#165219 — $dynamicRef support
- microsoft/vscode#155379 — Related schema improvements

## See Also

- `.github/instructions/typescript.instructions.md` — TypeScript implementation guide for Zod
- `.github/copilot-instructions.md` — General MCP tool guidelines
- `pyproject.toml` — Project configuration
