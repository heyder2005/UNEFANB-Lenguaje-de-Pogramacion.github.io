# utils/storage.py
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def load_json(name, default=None):
    p = DATA_DIR / f"{name}.json"
    if not p.exists():
        return default if default is not None else {}
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        return default if default is not None else {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default if default is not None else {}

def save_json(name, data):
    p = DATA_DIR / f"{name}.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
