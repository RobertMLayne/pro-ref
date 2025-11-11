
import os, requests, math, sys
from typing import Optional, Callable

class DownloadManager:
    """
    Simple resumable downloader using HTTP Range headers.
    """
    def __init__(self, session: Optional[requests.Session]=None, chunk_size=1024*512):
        self.session = session or requests.Session()
        self.chunk_size = chunk_size

    def download(self, url: str, dest_path: str, progress: Optional[Callable[[int,int], None]]=None) -> str:
        tmp_path = dest_path + ".part"
        headers = {}
        first_byte = 0
        if os.path.exists(tmp_path):
            first_byte = os.path.getsize(tmp_path)
            headers['Range'] = f"bytes={first_byte}-"
        with self.session.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            total = int(r.headers.get('Content-Length', '0'))
            mode = 'ab' if first_byte else 'wb'
            with open(tmp_path, mode) as f:
                downloaded = first_byte
                for chunk in r.iter_content(chunk_size=self.chunk_size):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress:
                        progress(downloaded, first_byte + total if total else downloaded)
        os.replace(tmp_path, dest_path)
        return dest_path
