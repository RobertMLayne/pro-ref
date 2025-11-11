"""Lightweight integration-style tests for the drop-in package."""

from __future__ import annotations

from pathlib import Path

import pytest

from api_gui.clients.uspto_odp import USPTOODPClient
from api_gui.util.provider_loader import load_providers

PROVIDERS_DIR = Path("src/api_gui/providers")


def test_provider_loader_discovers_operations() -> None:
    """Provider loader should surface the drop-in operations."""

    providers = load_providers(str(PROVIDERS_DIR))

    expected_keys = {
        "uspto_odp_pfw::pfw.search",
        "uspto_odp_pfw::pfw.bulk.products",
        "uspto_odp_pfw::pfw.list_documents",
        "uspto_odp_pfw::pfw.get_application",
        "uspto_odp_petition::petition.search",
    }

    assert expected_keys.issubset(providers.keys())


def test_client_applies_api_key_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """USPTO client should read API key environment variable on init."""

    monkeypatch.setenv("USPTO_ODP_API_KEY", "test-key")

    client = USPTOODPClient("https://api.uspto.gov", api_key_env="USPTO_ODP_API_KEY")

    assert client.session.headers["X-API-KEY"] == "test-key"


def test_client_base_url_normalization() -> None:
    """Client should normalise trailing slashes on the base URL."""

    client = USPTOODPClient("https://api.uspto.gov/", api_key_env=None)

    assert client.base_url == "https://api.uspto.gov"
