"""Tests for schema dialect configuration module."""

from __future__ import annotations

import os
from typing import Any

import pytest

from api_gui.util.schema_dialect import (
    ToolParameterSchema,
    add_schema_dialect,
    get_schema_dialect,
)


def test_get_schema_dialect_default() -> None:
    """Test that default dialect is draft-7."""
    # Clear env var if set
    if "FIRECRAWL_JSON_SCHEMA_DIALECT" in os.environ:
        del os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"]

    assert get_schema_dialect() == "draft-7"


def test_get_schema_dialect_from_env() -> None:
    """Test that dialect can be set via environment variable."""
    try:
        os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"] = "draft-2020-12"
        assert get_schema_dialect() == "draft-2020-12"

        os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"] = "draft-4"
        assert get_schema_dialect() == "draft-4"

        os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"] = "openapi-3.0"
        assert get_schema_dialect() == "openapi-3.0"
    finally:
        if "FIRECRAWL_JSON_SCHEMA_DIALECT" in os.environ:
            del os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"]


def test_get_schema_dialect_invalid() -> None:
    """Test that invalid dialect falls back to draft-7."""
    try:
        os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"] = "invalid-dialect"
        assert get_schema_dialect() == "draft-7"
    finally:
        if "FIRECRAWL_JSON_SCHEMA_DIALECT" in os.environ:
            del os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"]


def test_add_schema_dialect_draft7() -> None:
    """Test that draft-7 does not add $schema field."""
    if "FIRECRAWL_JSON_SCHEMA_DIALECT" in os.environ:
        del os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"]

    schema: dict[str, Any] = {"type": "object", "properties": {}}
    result = add_schema_dialect(schema)

    # Draft-7 should not add $schema field for VS Code compatibility
    assert "$schema" not in result


def test_add_schema_dialect_draft2020() -> None:
    """Test that draft-2020-12 adds $schema field."""
    try:
        os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"] = "draft-2020-12"

        schema: dict[str, Any] = {"type": "object", "properties": {}}
        result = add_schema_dialect(schema)

        expected = "https://json-schema.org/draft-2020-12/schema#"
        assert result["$schema"] == expected
    finally:
        if "FIRECRAWL_JSON_SCHEMA_DIALECT" in os.environ:
            del os.environ["FIRECRAWL_JSON_SCHEMA_DIALECT"]


def test_tool_parameter_schema_create() -> None:
    """Test creating a tool schema."""
    base_schema: dict[str, Any] = {
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"],
    }

    schema = ToolParameterSchema.create(base_schema)

    assert schema["type"] == "object"
    assert "url" in schema["properties"]
    assert "url" in schema["required"]


def test_tool_parameter_schema_from_dict() -> None:
    """Test building a tool schema from properties dict."""
    schema = ToolParameterSchema.from_dict(
        properties={
            "url": {"type": "string", "description": "The URL"},
            "timeout": {"type": "integer"},
        },
        required=["url"],
        description="Test parameters",
    )

    assert schema["type"] == "object"
    assert schema["description"] == "Test parameters"
    assert set(schema["required"]) == {"url"}
    assert "url" in schema["properties"]
    assert "timeout" in schema["properties"]


def test_tool_parameter_schema_without_required() -> None:
    """Test building a tool schema without required fields."""
    schema = ToolParameterSchema.from_dict(
        properties={"option": {"type": "string"}},
    )

    assert schema["type"] == "object"
    assert "required" not in schema or schema["required"] == []
    assert "option" in schema["properties"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
