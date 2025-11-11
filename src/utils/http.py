
import os, json, time, logging
from typing import Any, Dict, Optional
import requests

log = logging.getLogger(__name__)

class HttpClient:
    def __init__(self, base_url: str, api_key_env: Optional[str] = None, header_name: str = "X-API-KEY"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.api_key_env = api_key_env
        self.header_name = header_name

    def _headers(self, extra: Optional[Dict[str,str]] = None) -> Dict[str,str]:
        h = {"Accept": "application/json"}
        if self.api_key_env:
            key = os.getenv(self.api_key_env, "")
            if key:
                h[self.header_name] = key
        if extra:
            h.update(extra)
        return h

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        log.debug("GET %s params=%s", url, params)
        return self.session.get(url, headers=self._headers(), params=params, timeout=60)

    def post(self, path: str, json_body: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        log.debug("POST %s json=%s", url, json_body)
        return self.session.post(url, headers=self._headers({"Content-Type": "application/json"}), json=json_body or {}, timeout=60)
