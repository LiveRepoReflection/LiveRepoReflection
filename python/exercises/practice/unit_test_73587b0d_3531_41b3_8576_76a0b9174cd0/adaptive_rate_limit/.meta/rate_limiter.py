import time
import threading
import collections

class RateLimiter:
    def __init__(self):
        # Stores user configuration: user_id -> (configured_rate_limit, window_size_in_seconds)
        self.user_configs = {}
        # Stores user requests: user_id -> deque of request timestamps
        self.requests = {}
        # Lock to ensure thread-safe operations
        self.lock = threading.Lock()

    def set_user_rate_limit(self, user_id, rate_limit, window):
        with self.lock:
            self.user_configs[user_id] = (rate_limit, window)
            if user_id not in self.requests:
                self.requests[user_id] = collections.deque()
            else:
                # Clear previous request history when rate limit is reconfigured
                self.requests[user_id].clear()

    def check_request(self, user_id, timestamp, current_server_load, network_latency):
        with self.lock:
            # If user is not configured, set default rate limit to 10 requests per 60 seconds
            if user_id not in self.user_configs:
                default_rate = 10
                default_window = 60
                self.user_configs[user_id] = (default_rate, default_window)
                self.requests[user_id] = collections.deque()
            configured_limit, window = self.user_configs[user_id]

            # Adaptive throttling: reduce effective rate limit under high load or high latency
            # If server load is above 0.8 or network latency is above 300ms, use half the configured rate limit
            if current_server_load > 0.8 or network_latency > 300:
                effective_limit = max(1, configured_limit // 2)
            else:
                effective_limit = configured_limit

            # Get or create the request deque for the user
            dq = self.requests[user_id]
            # Remove timestamps that are older than the sliding window
            while dq and dq[0] <= timestamp - window:
                dq.popleft()

            # Check if current number of requests is below the effective rate limit
            if len(dq) < effective_limit:
                dq.append(timestamp)
                return True
            else:
                return False