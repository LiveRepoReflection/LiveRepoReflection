import time
import threading

_data_lock = threading.Lock()
_distributed_data = {}

class DistributedRateLimiter:
    def __init__(self, rate_limit, window_seconds):
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds

    def allow_request(self, client_id):
        current_time = time.time()
        with _data_lock:
            if client_id not in _distributed_data:
                _distributed_data[client_id] = {"window_start": current_time, "count": 0}
            client_record = _distributed_data[client_id]
            if current_time - client_record["window_start"] >= self.window_seconds:
                client_record["window_start"] = current_time
                client_record["count"] = 0
            if client_record["count"] < self.rate_limit:
                client_record["count"] += 1
                return True
            else:
                return False