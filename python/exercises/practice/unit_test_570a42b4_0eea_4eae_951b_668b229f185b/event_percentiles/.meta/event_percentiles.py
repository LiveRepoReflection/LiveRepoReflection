import threading
import bisect
import time
from collections import defaultdict, deque
from typing import List, Dict, Tuple

class WindowState:
    def __init__(self, accuracy: float):
        self.values = []
        self.sorted = False
        self.accuracy = accuracy
        self.max_size = int(1 / accuracy) * 100  # Heuristic for reasonable memory usage
        self.lock = threading.Lock()

    def add_value(self, value: float):
        with self.lock:
            if len(self.values) >= self.max_size:
                self.values.pop(0)
            self.values.append(value)
            self.sorted = False

    def get_percentile(self, percentile: float) -> float:
        with self.lock:
            if not self.values:
                return 0.0
            
            if not self.sorted:
                self.values.sort()
                self.sorted = True
            
            k = (len(self.values) - 1) * percentile
            f = int(k)
            c = int(k + 1)
            
            if c >= len(self.values):
                return self.values[-1]
            
            d = k - f
            return self.values[f] + (self.values[c] - self.values[f]) * d

class EventPercentiles:
    def __init__(self, window_sizes: List[int], percentiles: List[float], accuracy: float, max_event_age: int):
        self.window_sizes = sorted(window_sizes, reverse=True)
        self.percentiles = percentiles
        self.accuracy = accuracy
        self.max_event_age = max_event_age
        self.windows = {size: WindowState(accuracy) for size in window_sizes}
        self.event_queue = deque()
        self.lock = threading.Lock()
        self.last_cleanup = time.time()

    def process_event(self, timestamp: int, user_id: int, value: float):
        current_time = time.time()
        if timestamp < current_time - self.max_event_age:
            return

        with self.lock:
            self.event_queue.append((timestamp, value))
            self._cleanup_events(current_time)

        for window_size in self.window_sizes:
            if timestamp >= current_time - window_size:
                self.windows[window_size].add_value(value)

    def get_percentiles(self, timestamp: int) -> Dict[int, Dict[float, float]]:
        current_time = time.time()
        with self.lock:
            self._cleanup_events(current_time)

        results = {}
        for window_size, window_state in self.windows.items():
            window_results = {}
            for percentile in self.percentiles:
                window_results[percentile] = window_state.get_percentile(percentile)
            results[window_size] = window_results
        return results

    def _cleanup_events(self, current_time: float):
        if current_time - self.last_cleanup < 1.0:  # Cleanup at most once per second
            return

        while self.event_queue and self.event_queue[0][0] < current_time - max(self.window_sizes):
            self.event_queue.popleft()

        self.last_cleanup = current_time