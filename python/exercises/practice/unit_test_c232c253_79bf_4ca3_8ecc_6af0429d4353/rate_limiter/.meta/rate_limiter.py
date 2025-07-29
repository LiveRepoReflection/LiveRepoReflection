import time
from collections import deque
import threading
from typing import Dict, Tuple, Deque

class RateLimiter:
    def __init__(self):
        # Store client configurations: {client_id: (requests_allowed, window_seconds)}
        self._configs: Dict[str, Tuple[int, float]] = {}
        
        # Store request timestamps for each client: {client_id: deque of timestamps}
        self._requests: Dict[str, Deque[float]] = {}
        
        # Thread safety
        self._lock = threading.Lock()

    def configure(self, client_id: str, requests: int, window_seconds: float) -> None:
        """Configure rate limits for a client.
        
        Args:
            client_id: Unique identifier for the client
            requests: Number of requests allowed in the window
            window_seconds: Time window in seconds
        
        Raises:
            ValueError: If the configuration parameters are invalid
        """
        if requests <= 0:
            raise ValueError("Number of requests must be positive")
        if window_seconds <= 0:
            raise ValueError("Time window must be positive")

        with self._lock:
            self._configs[client_id] = (requests, window_seconds)
            # Reset existing requests for this client if any
            if client_id in self._requests:
                self._requests[client_id].clear()

    def allow_request(self, client_id: str) -> bool:
        """Check if a request should be allowed for the given client.
        
        Args:
            client_id: Unique identifier for the client
        
        Returns:
            bool: True if request is allowed, False if it should be blocked
        
        Raises:
            ValueError: If the client is not configured
        """
        if client_id not in self._configs:
            raise ValueError(f"Client {client_id} not configured")

        with self._lock:
            current_time = time.time()
            
            # Get client's configuration
            requests_allowed, window_seconds = self._configs[client_id]
            
            # Initialize request queue if needed
            if client_id not in self._requests:
                self._requests[client_id] = deque()
            
            request_times = self._requests[client_id]
            
            # Remove expired timestamps
            while request_times and current_time - request_times[0] > window_seconds:
                request_times.popleft()
            
            # Check if we're at the limit
            if len(request_times) >= requests_allowed:
                return False
            
            # Allow the request and record the timestamp
            request_times.append(current_time)
            return True

    def get_remaining_requests(self, client_id: str) -> int:
        """Get the number of remaining requests allowed for the client.
        
        Args:
            client_id: Unique identifier for the client
        
        Returns:
            int: Number of remaining requests allowed in the current window
        
        Raises:
            ValueError: If the client is not configured
        """
        if client_id not in self._configs:
            raise ValueError(f"Client {client_id} not configured")

        with self._lock:
            current_time = time.time()
            requests_allowed, window_seconds = self._configs[client_id]
            
            if client_id not in self._requests:
                return requests_allowed
            
            request_times = self._requests[client_id]
            
            # Remove expired timestamps
            while request_times and current_time - request_times[0] > window_seconds:
                request_times.popleft()
            
            return max(0, requests_allowed - len(request_times))

    def reset(self, client_id: str) -> None:
        """Reset the request counter for a client.
        
        Args:
            client_id: Unique identifier for the client
        
        Raises:
            ValueError: If the client is not configured
        """
        if client_id not in self._configs:
            raise ValueError(f"Client {client_id} not configured")

        with self._lock:
            if client_id in self._requests:
                self._requests[client_id].clear()