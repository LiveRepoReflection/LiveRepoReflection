from .event_aggregator import EventAggregator
import time
import heapq

class AdvancedEventAggregator(EventAggregator):
    def __init__(self, time_window_seconds=60, max_events_per_window=1000):
        super().__init__()
        self.time_window_seconds = time_window_seconds
        self.max_events_per_window = max_events_per_window
        self.window_counts = defaultdict(lambda: defaultdict(int))
        self.window_start = time.time()
        
    def process_event(self, event_type, region, timestamp):
        current_time = time.time()
        if current_time - self.window_start > self.time_window_seconds:
            self._rotate_window(current_time)
            
        with self.lock:
            if self.window_counts[event_type][region] < self.max_events_per_window:
                bisect.insort(self.event_data[event_type][region], timestamp)
                self.window_counts[event_type][region] += 1
                
    def _rotate_window(self, current_time):
        with self.lock:
            self.window_start = current_time
            self.window_counts.clear()
            
    def get_top_regions(self, event_type, n=5):
        if event_type not in self.event_data:
            return []
            
        region_counts = [
            (region, len(timestamps))
            for region, timestamps in self.event_data[event_type].items()
        ]
        return heapq.nlargest(n, region_counts, key=lambda x: x[1])