
import json, os
from pathlib import Path
from typing import Any

DEFAULT_DIR = Path.home() / ".api-gui" / "presets"
DEFAULT_DIR.mkdir(parents=True, exist_ok=True)

def save_preset(name: str, payload: dict) -> str:
    path = DEFAULT_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return str(path)

def load_preset(name: str) -> dict:
    path = DEFAULT_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_presets() -> list[str]:
    return [p.stem for p in DEFAULT_DIR.glob("*.json")]
