import threading
import time

class RateLimiter:
    def __init__(self, default_limit, window, config=None):
        self.default_limit = default_limit
        self.window = window
        self.config = config if config is not None else {}
        self.lock = threading.Lock()
        # Dictionary structure: {(user_id, api_endpoint): {"start": timestamp, "count": int}}
        self.registry = {}

    def check_and_increment(self, user_id, api_endpoint):
        key = (user_id, api_endpoint)
        current_time = time.time()
        # Determine limit for this user/endpoint - use config if provided, else default
        limit = self.default_limit
        if self.config and key in self.config:
            limit = self.config[key]
            
        with self.lock:
            record = self.registry.get(key)
            if record is None:
                self.registry[key] = {"start": current_time, "count": 1}
                return True
            # Check if current window has expired.
            if current_time - record["start"] >= self.window:
                # Reset the window.
                self.registry[key] = {"start": current_time, "count": 1}
                return True
            else:
                if record["count"] < limit:
                    record["count"] += 1
                    return True
                else:
                    return False