"""Example usage for the schema dialect configuration helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from api_gui.util.schema_dialect import (
    ToolParameterSchema,
    add_schema_dialect,
    get_schema_dialect,
)


def example_scrape_tool() -> dict[str, Any]:
    """Return an example schema for a scrape tool.

    Returns:
        A JSON Schema-compliant mapping for scrape tool parameters.
    """

    input_schema = ToolParameterSchema.from_dict(
        properties={
            "url": {
                "type": "string",
                "format": "uri",
                "description": "The URL to scrape",
            },
            "wait_for": {
                "type": "string",
                "description": "CSS selector to wait for before returning.",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds. Defaults to 30.",
            },
        },
        required=["url"],
        description="Parameters for web page scraping",
    )

    return {
        "name": "scrape_page",
        "description": "Scrape the content of a web page",
        "inputSchema": input_schema,
    }


def example_search_tool() -> dict[str, Any]:
    """Return an example schema for a search tool.

    Returns:
        A JSON Schema-compliant mapping for search tool parameters.
    """

    base_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string",
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (1-100)",
                "minimum": 1,
                "maximum": 100,
            },
            "offset": {
                "type": "integer",
                "description": "Result offset for pagination",
                "minimum": 0,
            },
        },
        "required": ["query"],
        "description": "Search API parameters",
    }

    input_schema = add_schema_dialect(base_schema)

    return {
        "name": "search",
        "description": "Search for information",
        "inputSchema": input_schema,
    }


def print_dialect_info() -> None:
    """Print the currently configured dialect."""

    dialect = get_schema_dialect()
    print(f"Current JSON Schema dialect: {dialect}")
    print("(Override via FIRECRAWL_JSON_SCHEMA_DIALECT env var)")


def main() -> None:
    """Display example schemas for quick inspection."""

    print_dialect_info()

    print("Scrape tool schema:")
    print(json.dumps(example_scrape_tool(), indent=2))
    print()

    print("Search tool schema:")
    print(json.dumps(example_search_tool(), indent=2))


if __name__ == "__main__":
    main()
