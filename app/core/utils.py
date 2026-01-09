from uuid import uuid4
from datetime import datetime, timezone

def gen_uuid() -> str:
    return str(uuid4())

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def pick(d: dict, keys: list[str]) -> dict:
    return {k: d.get(k) for k in keys if k in d}

def normalize_bool(v):
    return bool(v) if v is not None else False
