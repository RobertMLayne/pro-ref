"""Tests for the EndNote export helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from api_gui.export import endnote_export


def map_to_endnote_fields(
    record: dict[str, Any], mapping: dict[str, Any]
) -> dict[str, Any]:
    """Typed wrapper around the exporter helper for test use."""

    func: Any = getattr(endnote_export, "map_to_endnote_fields")
    return cast(dict[str, Any], func(record, mapping))


MAPPING_PATH = Path("src/api_gui/export/endnote_field_map.uspto_pfw.json")


def test_endnote_field_mapping_basic_fields() -> None:
    """Ensure the mapping extracts core PFW fields."""

    work: dict[str, Any] = {
        "applicationNumberText": "14412875",
        "applicationMetaData": {
            "inventionTitle": "Sample Invention",
            "patentNumber": "US1234567B2",
            "filingDate": "2013-01-01",
            "grantDate": "2017-01-01",
            "groupArtUnitNumber": "1234",
            "inventorBag": [
                {"inventorNameText": "DOE, JOHN"},
            ],
        },
    }

    with MAPPING_PATH.open("r", encoding="utf-8") as handle:
        mapping: dict[str, Any] = json.load(handle)["transform"]

    result: dict[str, Any] = map_to_endnote_fields(work, mapping)

    assert result["Title"] == "Sample Invention"
    assert result["Patent Number"] == "US1234567B2"
    assert result["Application Number"] == "14412875"
    assert result["Inventors"] == "DOE, JOHN"
