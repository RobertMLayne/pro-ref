from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, cast

from api_gui.clients.uspto_odp import USPTOODPClient
from jsonschema import validate
from tests.conftest import recorder


SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "src" / "api_gui" / "schemas"
SCHEMA_PFW = SCHEMAS_DIR / "patent-data-schema.json"
SCHEMA_BULK = SCHEMAS_DIR / "bulkdata-response-schema.json"


def _client() -> USPTOODPClient:
    return USPTOODPClient(
        "https://api.uspto.gov",
        api_key_env="USPTO_ODP_API_KEY",
    )


def _load_schema(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return cast(Dict[str, Any], json.load(handle))


@recorder("pfw_lookup_14412875")
def test_lookup_application() -> None:
    cli = _client()
    data = cli.pfw_lookup("14412875")
    assert "patentFileWrapperDataBag" in data

    schema = _load_schema(SCHEMA_PFW)
    bag = data.get("patentFileWrapperDataBag")
    if isinstance(bag, list) and bag:
        entry = cast(Dict[str, Any], bag[0])
        subset: Dict[str, List[Dict[str, Any]]] = {"patentFileWrapperDataBag": [entry]}
        validate(subset, schema)


@recorder("pfw_documents_14412875")
def test_documents_list() -> None:
    cli = _client()
    data = cli.pfw_documents("14412875")
    assert "documentBag" in data

    schema = _load_schema(SCHEMA_PFW)
    bag = data.get("documentBag")
    if isinstance(bag, list) and bag:
        entry = cast(Dict[str, Any], bag[0])
        subset: Dict[str, List[Dict[str, Any]]] = {"documentBag": [entry]}
        validate(subset, schema)


@recorder("bulk_list_ptfwprd")
def test_bulk_list_prd() -> None:
    cli = _client()
    data = cli.bulk_products("PTFWPRD", latest=True)
    assert "bulkDataProductBag" in data

    schema = _load_schema(SCHEMA_BULK)
    bag = data.get("bulkDataProductBag")
    if isinstance(bag, list) and bag:
        entry = cast(Dict[str, Any], bag[0])
        subset: Dict[str, List[Dict[str, Any]]] = {"bulkDataProductBag": [entry]}
        validate(subset, schema)
