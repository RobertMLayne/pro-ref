from __future__ import annotations

from typing import Any, Dict, Mapping

from .base import BaseClient
from ..util.download_manager import DownloadManager

JsonDict = Dict[str, Any]


class USPTOODPClient(BaseClient):
    def search_pfw(self, payload: Mapping[str, Any]) -> JsonDict:
        response = self.post(
            "/api/v1/patent/applications/search",
            json_body=payload,
        )
        return response.json()

    def search_pfw_get(self, params: Mapping[str, Any]) -> JsonDict:
        response = self.get(
            "/api/v1/patent/applications/search",
            params=params,
        )
        return response.json()

    def pfw_lookup(self, application_number: str) -> JsonDict:
        endpoint = f"/api/v1/patent/applications/{application_number}"
        response = self.get(endpoint)
        return response.json()

    def pfw_documents(self, application_number: str) -> JsonDict:
        endpoint = f"/api/v1/patent/applications/{application_number}/documents"
        response = self.get(endpoint)
        return response.json()

    def pfw_download(
        self,
        application_number: str,
        document_id: str,
        ext: str,
        dest_path: str,
    ) -> str:
        endpoint = (
            f"/api/v1/download/applications/{application_number}/{document_id}.{ext}"
        )
        url = self._url(endpoint)
        manager = DownloadManager(self.session)
        return manager.download(url, dest_path)

    def bulk_products(self, product_id: str, latest: bool = True) -> JsonDict:
        params: Dict[str, str] = {"latest": "true"} if latest else {}
        endpoint = f"/api/v1/datasets/products/{product_id}"
        response = self.get(endpoint, params=params)
        return response.json()

    def bulk_download(
        self,
        product_id: str,
        file_name: str,
        dest_path: str,
    ) -> str:
        endpoint = f"/api/v1/datasets/products/files/{product_id}/{file_name}"
        url = self._url(endpoint)
        manager = DownloadManager(self.session)
        return manager.download(url, dest_path)
