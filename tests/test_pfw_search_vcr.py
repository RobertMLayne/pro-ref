from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, cast

import pytest

from api_gui.clients.base import ApiError
from api_gui.clients.uspto_odp import USPTOODPClient
from jsonschema import validate
from tests.conftest import recorder


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "api_gui"
    / "schemas"
    / "patent-data-schema.json"
)


def _client() -> USPTOODPClient:
    return USPTOODPClient(
        "https://api.uspto.gov",
        api_key_env="USPTO_ODP_API_KEY",
    )


def _load_schema() -> Dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@recorder("pfw_simple_search")
def test_pfw_simple_search() -> None:
    cli = _client()
    payload: Dict[str, Any] = {
        "q": "applicationMetaData.applicationTypeLabelName:Utility",
        "pagination": {"offset": 0, "limit": 1},
        "facets": ["applicationMetaData.applicationTypeLabelName"],
    }
    data = cli.search_pfw(payload)
    assert "patentFileWrapperDataBag" in data

    schema = _load_schema()
    bag = data.get("patentFileWrapperDataBag")
    if isinstance(bag, list) and bag:
        entry = cast(Dict[str, Any], bag[0])
        subset: Dict[str, List[Dict[str, Any]]] = {"patentFileWrapperDataBag": [entry]}
        validate(subset, schema)


@recorder("pfw_get_error_case")
def test_pfw_get_error_case() -> None:
    cli = _client()
    with pytest.raises(ApiError):
        cli.search_pfw_get({"q": '"Patented Case"'})
