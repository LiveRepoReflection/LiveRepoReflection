import threading
import collections
import statistics
import math

class ConcurrentStreamAnalyzer:
    def __init__(self, window_size: int, num_sources: int):
        if window_size <= 0:
            raise ValueError("window_size must be a positive integer")
        if num_sources <= 0:
            raise ValueError("num_sources must be a positive integer")
        self.window_size = window_size
        self.num_sources = num_sources
        # Using deque with fixed maxlen ensures automatic eviction of the oldest value.
        self.window = collections.deque(maxlen=window_size)
        self.lock = threading.Lock()

    def process_data(self, source_id: int, data_point: float):
        if not (0 <= source_id < self.num_sources):
            raise ValueError("Invalid source_id")
        with self.lock:
            self.window.append(data_point)

    def get_statistics(self) -> dict:
        with self.lock:
            # Create a copy to avoid holding the lock during potentially long computation
            window_snapshot = list(self.window)

        if not window_snapshot:
            return {
                "mean": None,
                "median": None,
                "std_dev": None,
                "min": None,
                "max": None
            }

        mean_val = statistics.mean(window_snapshot)
        median_val = statistics.median(window_snapshot)
        min_val = min(window_snapshot)
        max_val = max(window_snapshot)
        
        # For sample standard deviation, if there is less than 2 elements, return None.
        if len(window_snapshot) < 2:
            std_dev_val = None
        else:
            # Use sample standard deviation (Bessel's correction)
            std_dev_val = statistics.stdev(window_snapshot)
        
        return {
            "mean": mean_val,
            "median": median_val,
            "std_dev": std_dev_val,
            "min": min_val,
            "max": max_val
        }