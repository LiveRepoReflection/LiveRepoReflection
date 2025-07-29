import time
import threading
from collections import defaultdict
from typing import Dict, List, Tuple

class SlidingRateLimiter:
    def __init__(self):
        self.limits: Dict[str, Tuple[int, int]] = {}  # client_id: (max_requests, window_size)
        self.requests: Dict[str, List[Tuple[int, int]]] = defaultdict(list)  # client_id: [(timestamp, count)]
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str, request_timestamp: int) -> bool:
        with self.lock:
            if client_id not in self.limits:
                return False
                
            max_requests, window_size = self.limits[client_id]
            current_time = request_timestamp
            
            # Remove expired requests
            self._cleanup_old_requests(client_id, current_time, window_size)
            
            # Calculate total requests in window
            total = sum(count for _, count in self.requests[client_id])
            
            if total >= max_requests:
                return False
                
            # Add current request
            self.requests[client_id].append((current_time, 1))
            return True
    
    def update_limit(self, client_id: str, new_limit: int, window_size: int) -> None:
        with self.lock:
            self.limits[client_id] = (new_limit, window_size)
            # Clean up old requests when updating limits
            if client_id in self.requests:
                self._cleanup_old_requests(client_id, time.time(), window_size)
    
    def _cleanup_old_requests(self, client_id: str, current_time: int, window_size: int) -> None:
        if client_id not in self.requests:
            return
            
        cutoff = current_time - window_size
        self.requests[client_id] = [
            (ts, count) for ts, count in self.requests[client_id] 
            if ts >= cutoff
        ]