from __future__ import annotations

import os
from typing import Any, Mapping

import requests


class ApiError(Exception):
    """Raised when a USPTO API request fails."""


class BaseClient:
    """HTTP client wrapper that handles authentication and error cases."""

    def __init__(
        self,
        base_url: str,
        api_key_env: str | None = None,
        api_key_header: str = "X-API-KEY",
        timeout: float = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        self.api_key_env = api_key_env
        self.api_key_header = api_key_header

        if api_key_env:
            key = os.getenv(api_key_env, "")
            if key:
                self.session.headers[self.api_key_header] = key

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        url = self._url(path)
        response = self.session.get(url, params=params, timeout=self.timeout)
        if not response.ok:
            snippet = response.text[:200]
            raise ApiError(f"GET {url} failed: {response.status_code} {snippet}")
        return response

    def post(
        self,
        path: str,
        json_body: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        url = self._url(path)
        payload = dict(json_body) if json_body is not None else {}
        response = self.session.post(url, json=payload, timeout=self.timeout)
        if not response.ok:
            snippet = response.text[:200]
            raise ApiError(f"POST {url} failed: {response.status_code} {snippet}")
        return response
