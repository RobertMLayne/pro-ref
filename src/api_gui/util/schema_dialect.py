"""Helpers for configuring JSON Schema dialect support."""

from __future__ import annotations

import logging
import os
from typing import Any, Literal

SchemaDialect = Literal["draft-7", "draft-2020-12", "draft-4", "openapi-3.0"]

_LOGGER = logging.getLogger(__name__)


def get_schema_dialect() -> SchemaDialect:
    """Return the configured JSON Schema dialect.

    The value defaults to ``draft-7`` for compatibility with VS Code's JSON
    validator. Set the ``FIRECRAWL_JSON_SCHEMA_DIALECT`` environment variable to
    opt into another supported dialect.

    Returns:
        The configured dialect, falling back to ``draft-7`` when an unsupported
        value is supplied.
    """

    dialect = os.getenv("FIRECRAWL_JSON_SCHEMA_DIALECT", "draft-7")

    valid_dialects: tuple[SchemaDialect, ...] = (
        "draft-7",
        "draft-2020-12",
        "draft-4",
        "openapi-3.0",
    )

    if dialect not in valid_dialects:
        _LOGGER.warning(
            "Unsupported schema dialect '%s'; falling back to draft-7. "
            "Valid options are: %s",
            dialect,
            ", ".join(valid_dialects),
        )
        return "draft-7"

    return dialect


def add_schema_dialect(schema: dict[str, Any]) -> dict[str, Any]:
    """Attach dialect metadata to ``schema`` when required.

    Args:
        schema: The JSON Schema definition to augment.

    Returns:
        The provided schema with ``$schema`` metadata when the configured
        dialect is newer than draft-7.
    """

    dialect = get_schema_dialect()

    if dialect != "draft-7":
        schema["$schema"] = f"https://json-schema.org/{dialect}/schema#"

    return schema


class ToolParameterSchema:
    """Helper for building MCP tool schemas that respect dialect settings."""

    @staticmethod
    def create(schema: dict[str, Any]) -> dict[str, Any]:
        """Return ``schema`` with dialect metadata applied."""

        return add_schema_dialect(schema)

    @staticmethod
    def from_dict(
        properties: dict[str, Any],
        required: list[str] | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Build an object schema from ``properties``.

        Args:
            properties: Mapping of parameter names to JSON Schema fragments.
            required: Names of parameters that must be supplied.
            description: Optional human-readable description of the schema.

        Returns:
            An object schema with dialect metadata applied.
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


__all__ = [
    "SchemaDialect",
    "get_schema_dialect",
    "add_schema_dialect",
    "ToolParameterSchema",
]
