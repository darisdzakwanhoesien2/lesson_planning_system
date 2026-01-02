import json
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_index(index_path: Path):
    data = load_json(index_path)
    return data if isinstance(data, list) else []


def list_json_files(dir_path: Path):
    if not dir_path.exists():
        return []
    return sorted(dir_path.glob("*.json"))
