import json, time, uuid, os, threading
from typing import Optional, Dict, Any, List

QUEUE_DIR = os.environ.get("RM_QUEUE_DIR", "runtime/queues")

def _ensure():
    os.makedirs(QUEUE_DIR, exist_ok=True)

def enqueue(channel: str, payload: Dict[str, Any]) -> str:
    _ensure()
    msg_id = f"{int(time.time()*1000)}-{uuid.uuid4().hex}"
    path = os.path.join(QUEUE_DIR, f"{channel}__{msg_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return msg_id

def poll(channel: str, since: float=0.0) -> List[Dict[str, Any]]:
    _ensure()
    items = []
    for name in sorted(os.listdir(QUEUE_DIR)):
        if not name.startswith(f"{channel}__") or not name.endswith(".json"):
            continue
        full = os.path.join(QUEUE_DIR, name)
        if os.path.getmtime(full) >= since:
            with open(full, "r", encoding="utf-8") as f:
                items.append(json.load(f))
    return items
