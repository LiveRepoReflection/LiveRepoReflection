import time
import threading
import math

class RateLimiter:
    def __init__(self, limit, window):
        self.limit = limit
        self.window = window
        self.lock = threading.Lock()
        # Dictionary mapping user_id to a tuple (window_start, count)
        self.user_data = {}

    def _get_window_start(self, current_time):
        # Calculate the start time of the current window
        return math.floor(current_time / self.window) * self.window

    def allow_request(self, user_id, current_time):
        window_start = self._get_window_start(current_time)
        with self.lock:
            if user_id in self.user_data:
                stored_window_start, count = self.user_data[user_id]
                # If the current request timestamp falls in the same window as stored window
                if window_start == stored_window_start:
                    if count < self.limit:
                        self.user_data[user_id] = (stored_window_start, count + 1)
                        return True
                    else:
                        return False
                else:
                    # For non-monotonic timestamps, if the provided current_time belongs to an earlier window 
                    # than the stored one, we return False as the record already exists for a later window.
                    if window_start < stored_window_start:
                        return False
                    # Reset count for the new window.
                    self.user_data[user_id] = (window_start, 1)
                    return True
            else:
                self.user_data[user_id] = (window_start, 1)
                return True