"""
Example usage of the schema dialect configuration module.

This demonstrates how to use the configurable JSON Schema dialect
support for MCP tool parameters and other integrations.
"""

import sys
from pathlib import Path
from typing import Any

# Add parent directory to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from schema_dialect import (
    ToolParameterSchema,
    get_schema_dialect,
    add_schema_dialect,
)


def example_scrape_tool() -> dict[str, Any]:
    """
    Example: Define a web scraping tool with configurable schema dialect.

    Shows how to use ToolParameterSchema to create consistent parameter
    schemas that work across different dialect versions.
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
                "description": ("CSS selector to wait for before returning. Optional."),
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
    """
    Example: Define a search tool using inline schema creation.

    Demonstrates creating a schema from a dict then wrapping it
    with dialect support.
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

    # Add dialect support (draft-7 by default, or override)
    input_schema = add_schema_dialect(base_schema)

    return {
        "name": "search",
        "description": "Search for information",
        "inputSchema": input_schema,
    }


def print_dialect_info() -> None:
    """Print the current schema dialect configuration."""
    dialect = get_schema_dialect()
    print(f"Current JSON Schema dialect: {dialect}")
    print("(Override via FIRECRAWL_JSON_SCHEMA_DIALECT env var)")
    print()


if __name__ == "__main__":
    print_dialect_info()

    print("Scrape tool schema:")
    scrape_tool = example_scrape_tool()
    import json

    print(json.dumps(scrape_tool, indent=2))
    print()

    print("Search tool schema:")
    search_tool = example_search_tool()
    print(json.dumps(search_tool, indent=2))
