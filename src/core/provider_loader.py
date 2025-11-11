
import json, os, glob
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Provider:
    id: str
    meta: Dict[str, Any]

class ProviderRegistry:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.providers: Dict[str, Provider] = {}

    def load_all(self) -> None:
        for path in glob.glob(os.path.join(self.base_dir, "*.json")):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            pid = data.get("provider") + ":" + data.get("operation", {}).get("op_id", "op")
            self.providers[pid] = Provider(id=pid, meta=data)

    def list(self) -> List[str]:
        return sorted(self.providers.keys())

    def get(self, pid: str) -> Dict[str, Any]:
        return self.providers[pid].meta
