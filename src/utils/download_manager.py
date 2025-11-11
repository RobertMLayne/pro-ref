
import os, requests
from typing import Optional, Callable

CHUNK = 1024 * 256

def download_with_resume(url: str, dest_path: str, headers: Optional[dict] = None, progress: Optional[Callable[[int, Optional[int]], None]] = None):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    temp_path = dest_path + ".part"
    resume_pos = 0
    if os.path.exists(temp_path):
        resume_pos = os.path.getsize(temp_path)
    req_headers = headers.copy() if headers else {}
    if resume_pos:
        req_headers["Range"] = f"bytes={resume_pos}-"
    with requests.get(url, headers=req_headers, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", "0")) + resume_pos if r.headers.get("Content-Length") else None
        mode = "ab" if resume_pos else "wb"
        with open(temp_path, mode) as f:
            downloaded = resume_pos
            for chunk in r.iter_content(CHUNK):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if progress:
                    progress(downloaded, total)
    os.replace(temp_path, dest_path)
