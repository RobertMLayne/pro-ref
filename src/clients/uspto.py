
from typing import Any, Dict, Optional
from utils.http import HttpClient

class USPTOClient:
    def __init__(self, base_url: str = "https://api.uspto.gov", api_key_env: str = "USPTO_ODP_API_KEY"):
        self.http = HttpClient(base_url, api_key_env)

    # PFW search
    def pfw_search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.http.post("/api/v1/patent/applications/search", payload)
        r.raise_for_status()
        return r.json()

    def pfw_search_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        r = self.http.get("/api/v1/patent/applications/search", params=params)
        r.raise_for_status()
        return r.json()

    def pfw_download_small(self, payload: Dict[str, Any]) -> bytes:
        r = self.http.post("/api/v1/patent/applications/search/download", payload)
        r.raise_for_status()
        return r.content

    def pfw_lookup(self, application_number: str) -> Dict[str, Any]:
        r = self.http.get(f"/api/v1/patent/applications/{application_number}")
        r.raise_for_status()
        return r.json()

    def pfw_documents(self, application_number: str) -> Dict[str, Any]:
        r = self.http.get(f"/api/v1/patent/applications/{application_number}/documents")
        r.raise_for_status()
        return r.json()

    # Bulk
    def bulk_products(self, product_identifier: str, latest: bool = True) -> Dict[str, Any]:
        r = self.http.get(f"/api/v1/datasets/products/{product_identifier}", params={"latest": str(latest).lower()})
        r.raise_for_status()
        return r.json()

    # Petition Decisions
    def petition_search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.http.post("/api/v1/petition/decisions/search", payload)
        r.raise_for_status()
        return r.json()

    def petition_lookup(self, record_identifier: str) -> Dict[str, Any]:
        r = self.http.get(f"/api/v1/petition/decisions/{record_identifier}")
        r.raise_for_status()
        return r.json()
