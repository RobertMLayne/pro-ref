
import json, os, glob
from dataclasses import dataclass
from typing import Any

@dataclass
class Provider:
    key: str
    meta: dict

def load_providers(dir_path: str) -> dict[str, Provider]:
    out = {}
    for fp in glob.glob(os.path.join(dir_path, "provider.*.json")):
        with open(fp, "r", encoding="utf-8") as f:
            meta = json.load(f)
        key = f"{meta.get('provider')}::{meta['operation']['op_id']}"
        out[key] = Provider(key=key, meta=meta)
    return out
