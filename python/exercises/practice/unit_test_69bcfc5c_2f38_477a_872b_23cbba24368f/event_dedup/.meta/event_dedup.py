import json
import threading
import time
import heapq

_dedup_window = 1.0
_event_store = {}
_exp_heap = []
_lock = threading.Lock()

def _cleanup():
    now = time.time()
    while _exp_heap and _exp_heap[0][0] <= now:
        exp_time, event_id = heapq.heappop(_exp_heap)
        if _event_store.get(event_id, 0) == exp_time:
            del _event_store[event_id]

def ingest_event(event: str) -> bool:
    try:
        event_obj = json.loads(event)
    except Exception:
        raise ValueError("Invalid JSON")
    if "event_id" not in event_obj:
        raise ValueError("Missing event_id")
    event_id = event_obj["event_id"]
    now = time.time()
    expiration = now + _dedup_window
    with _lock:
        _cleanup()
        if event_id in _event_store and _event_store[event_id] > now:
            return False
        _event_store[event_id] = expiration
        heapq.heappush(_exp_heap, (expiration, event_id))
    return True

def reset_store():
    global _event_store, _exp_heap
    with _lock:
        _event_store = {}
        _exp_heap = []

def set_dedup_window(new_window: float):
    global _dedup_window
    with _lock:
        _dedup_window = new_window