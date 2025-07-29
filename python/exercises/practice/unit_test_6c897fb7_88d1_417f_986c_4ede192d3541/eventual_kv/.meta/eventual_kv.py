import time
import threading
from typing import Dict, Optional, Tuple

class Node:
    def __init__(self):
        # Store key-value pairs with timestamps
        # Format: {key: (value, timestamp)}
        self._store: Dict[str, Tuple[str, float]] = {}
        self._lock = threading.Lock()

    def put(self, key: str, value: str) -> None:
        """
        Store a key-value pair with current timestamp.
        Thread-safe operation.
        """
        with self._lock:
            timestamp = time.time()
            self._store[key] = (value, timestamp)

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve value for a given key.
        Returns None if key doesn't exist.
        Thread-safe operation.
        """
        with self._lock:
            if key in self._store:
                return self._store[key][0]
            return None

    def get_all_data(self) -> Dict[str, Tuple[str, float]]:
        """
        Return all key-value pairs with their timestamps.
        Thread-safe operation.
        """
        with self._lock:
            return dict(self._store)

    def replicate(self, data: Dict[str, Tuple[str, float]]) -> None:
        """
        Merge received data with local storage using LWW strategy.
        Only updates entries that have newer timestamps.
        Thread-safe operation.
        """
        with self._lock:
            for key, (value, timestamp) in data.items():
                # If key doesn't exist locally or remote timestamp is newer
                if (key not in self._store or 
                    timestamp > self._store[key][1]):
                    self._store[key] = (value, timestamp)