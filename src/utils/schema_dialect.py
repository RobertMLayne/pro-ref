"""
JSON Schema dialect configuration for tool parameters.

Resolves VS Code JSON validator compatibility issues by defaulting to
draft-7 while allowing power users to opt in to newer dialects via
environment variable.

This module provides helpers for generating JSON schemas with configurable
dialects for MCP (Model Context Protocol) tools and other integrations.

See: https://github.com/microsoft/vscode/issues/251315 (draft-2020-12 support)
"""

import os
from typing import Any, Literal

SchemaDialect = Literal["draft-7", "draft-2020-12", "draft-4", "openapi-3.0"]


def get_schema_dialect() -> SchemaDialect:
    """
    Get the configured JSON Schema dialect.

    Defaults to draft-7 for compatibility with current VS Code.
    Override via FIRECRAWL_JSON_SCHEMA_DIALECT environment variable.

    Returns:
        The schema dialect to use when generating JSON Schema.
    """
    dialect = os.getenv("FIRECRAWL_JSON_SCHEMA_DIALECT", "draft-7")

    valid_dialects: tuple[SchemaDialect, ...] = (
        "draft-7",
        "draft-2020-12",
        "draft-4",
        "openapi-3.0",
    )

    if dialect not in valid_dialects:
        print(
            f"Warning: Invalid schema dialect '{dialect}'. "
            f"Supported values: {', '.join(valid_dialects)}. "
            f"Falling back to draft-7."
        )
        return "draft-7"

    return dialect  # type: ignore


def add_schema_dialect(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Add JSON Schema dialect information to a schema dict.

    For draft-2020-12 and higher dialects, this adds the $schema field.
    For draft-7 (default), the field is omitted for compatibility.

    Args:
        schema: The JSON schema dict to augment.

    Returns:
        The schema dict with $schema field added (if not draft-7).

    Example:
        ```python
        schema = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
            },
            "required": ["url"],
        }
        schema = add_schema_dialect(schema)
        # If FIRECRAWL_JSON_SCHEMA_DIALECT=draft-2020-12, adds:
        # schema["$schema"] = "https://json-schema.org/draft-2020-12/schema"
        ```
    """
    dialect = get_schema_dialect()

    # Only add $schema for dialects newer than draft-7
    if dialect != "draft-7":
        schema["$schema"] = f"https://json-schema.org/{dialect}/schema#"

    return schema


class ToolParameterSchema:
    """
    Helper for generating MCP tool parameter schemas with dialect support.

    Use this when defining tool parameters to ensure consistent JSON Schema
    generation across all tools, with configurable dialect support.

    The schema is automatically augmented with the configured dialect
    information (or omitted for draft-7 to maintain VS Code compatibility).

    Example:
        ```python
        # Define your tool's input parameters
        scrape_input = {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "The URL to scrape",
                },
                "wait_for": {
                    "type": "string",
                    "description": "CSS selector to wait for (optional)",
                },
            },
            "required": ["url"],
        }

        # Wrap with dialect support
        tool_schema = ToolParameterSchema.create(scrape_input)

        # Register the tool with MCP
        tool = {
            "name": "scrape_page",
            "description": "Scrape a web page",
            "inputSchema": tool_schema,
        }
        ```
    """

    @staticmethod
    def create(schema: dict[str, Any]) -> dict[str, Any]:
        """
        Create a tool parameter schema with dialect support.

        Args:
            schema: The base JSON schema dict.

        Returns:
            Schema augmented with configured dialect information.
        """
        return add_schema_dialect(schema)

    @staticmethod
    def from_dict(
        properties: dict[str, Any],
        required: list[str] | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """
        Build a tool parameter schema from property definitions.

        Args:
            properties: Dict mapping parameter names to their schemas.
            required: List of required parameter names.
            description: Optional description for the whole object.

        Returns:
            A complete JSON schema dict with dialect support.

        Example:
            ```python
            schema = ToolParameterSchema.from_dict(
                properties={
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Page URL",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                    },
                },
                required=["url"],
                description="Input parameters for web scraping",
            )
            ```
        """
        schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        if description:
            schema["description"] = description

        return add_schema_dialect(schema)
