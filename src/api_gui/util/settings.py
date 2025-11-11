
import json, os
from pathlib import Path

CONFIG_DIR = Path.home() / ".api-gui"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_PATH = CONFIG_DIR / "settings.json"

DEFAULTS = {
  "api_keys": {
    "uspto_odp": ""
  },
  "theme": "lumenci_light",
  "attachment_policy": "url"  # url | file | none
}

def load_settings():
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULTS)
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # merge defaults
    merged = {**DEFAULTS, **data}
    merged["api_keys"] = {**DEFAULTS["api_keys"], **merged.get("api_keys", {})}
    return merged

def save_settings(data):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return str(SETTINGS_PATH)
