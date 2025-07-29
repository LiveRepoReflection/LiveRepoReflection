import threading
import time
import json
import os
from collections import defaultdict
from typing import Dict, Optional

class DistributedCounter:
    def __init__(self, expiry_seconds: Optional[int] = None, persistence_file: str = "counter_state.json"):
        self._counts = defaultdict(int)
        self._lock = threading.Lock()
        self._last_updated: Dict[str, float] = {}
        self.expiry_seconds = expiry_seconds
        self.persistence_file = persistence_file
        self._load_persisted_state()
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_keys, daemon=True)
        self._cleanup_thread.start()

    def process_event(self, key: str, delta: int) -> None:
        with self._lock:
            self._counts[key] += delta
            if self.expiry_seconds is not None:
                self._last_updated[key] = time.time()

    def get_count(self, key: str) -> int:
        with self._lock:
            if self.expiry_seconds is not None:
                last_updated = self._last_updated.get(key)
                if last_updated and (time.time() - last_updated) > self.expiry_seconds:
                    del self._counts[key]
                    del self._last_updated[key]
                    return 0
            return self._counts.get(key, 0)

    def _cleanup_expired_keys(self) -> None:
        while True:
            time.sleep(60)  # Run cleanup once per minute
            if self.expiry_seconds is None:
                continue

            with self._lock:
                current_time = time.time()
                expired_keys = [
                    key for key, timestamp in self._last_updated.items()
                    if (current_time - timestamp) > self.expiry_seconds
                ]
                for key in expired_keys:
                    del self._counts[key]
                    del self._last_updated[key]

    def _persist_counts(self) -> None:
        with self._lock:
            state = {
                'counts': dict(self._counts),
                'last_updated': self._last_updated
            }
            with open(self.persistence_file, 'w') as f:
                json.dump(state, f)

    def _load_persisted_state(self) -> None:
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, 'r') as f:
                    state = json.load(f)
                    self._counts = defaultdict(int, state.get('counts', {}))
                    self._last_updated = state.get('last_updated', {})
            except (json.JSONDecodeError, IOError):
                pass

    def __del__(self):
        self._persist_counts()