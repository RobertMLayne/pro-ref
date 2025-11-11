from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "api_gui"
    / "schemas"
    / "petition-decision-schema.json"
)


def test_petition_schema_loads() -> None:
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    schema: Dict[str, Any] = json.loads(schema_text)
    properties = schema.get("properties", {})
    assert "petitionDecisionDataBag" in properties
