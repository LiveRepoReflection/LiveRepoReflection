import time
import threading
from collections import defaultdict, deque
from typing import Dict, Deque

class RateLimiter:
    def __init__(self, max_requests: int, time_window_seconds: int):
        self.max_requests = max_requests
        self.time_window = time_window_seconds
        self.client_queues: Dict[str, Deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()
        
    def allow_request(self, client_id: str, request) -> bool:
        current_time = time.time()
        request_time = request.timestamp if hasattr(request, 'timestamp') else current_time
        
        with self.lock:
            # Clean up old requests outside the time window
            while (self.client_queues[client_id] and 
                   request_time - self.client_queues[client_id][0] > self.time_window):
                self.client_queues[client_id].popleft()
            
            # Check if we can allow the new request
            if len(self.client_queues[client_id]) < self.max_requests:
                self.client_queues[client_id].append(request_time)
                return True
            return False
    
    def clear_client(self, client_id: str):
        with self.lock:
            if client_id in self.client_queues:
                del self.client_queues[client_id]