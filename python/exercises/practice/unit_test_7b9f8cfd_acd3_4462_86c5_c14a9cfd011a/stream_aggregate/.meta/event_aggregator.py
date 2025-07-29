import bisect
from collections import defaultdict
import threading

class EventAggregator:
    def __init__(self):
        self.lock = threading.Lock()
        self.event_data = defaultdict(lambda: defaultdict(list))
        
    def process_event(self, event_type, region, timestamp):
        with self.lock:
            bisect.insort(self.event_data[event_type][region], timestamp)
            
    def query_event_count(self, event_type, region, start_timestamp, end_timestamp):
        if event_type not in self.event_data or region not in self.event_data[event_type]:
            return 0
            
        timestamps = self.event_data[event_type][region]
        left = bisect.bisect_left(timestamps, start_timestamp)
        right = bisect.bisect_right(timestamps, end_timestamp)
        return right - left

    def get_all_events(self):
        return self.event_data