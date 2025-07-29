import bisect
import threading
import time

class EventAggregator:
    def __init__(self, window, error_bound):
        # window: sliding window size in milliseconds
        # error_bound: allowed error percentage for approximate median (not used in exact calculation)
        self.window = window
        self.error_bound = error_bound
        # For each category, maintain a list of (timestamp, value) tuples
        # Sorted by timestamp for easier sliding window management.
        self.events = {}
        self.lock = threading.Lock()

    def add_event(self, event):
        # event is a tuple: (timestamp, category, value, node_id)
        timestamp, category, value, node_id = event
        with self.lock:
            if category not in self.events:
                self.events[category] = []
            # Insert preserving order by timestamp, useful if events are generally in-order.
            # If events are out-of-order, binary insertion ensures list remains sorted.
            bisect.insort(self.events[category], (timestamp, value))

    def get_median(self, category, current_time):
        # Returns the approximate median event value for the given category for events within the sliding window.
        with self.lock:
            if category not in self.events:
                return None

            # Determine the threshold; only events with timestamp >= threshold are valid.
            threshold = current_time - self.window
            events_list = self.events[category]

            # Find the starting index for events within the sliding window using binary search.
            left_index = 0
            right_index = len(events_list)
            while left_index < right_index:
                mid = (left_index + right_index) // 2
                if events_list[mid][0] < threshold:
                    left_index = mid + 1
                else:
                    right_index = mid

            # Only consider events from left_index onward.
            valid_events = events_list[left_index:]
            if not valid_events:
                return None

            # Clean up old events to free memory; remove events before left_index.
            if left_index > 0:
                self.events[category] = valid_events

            # Extract the values
            values = [value for (_, value) in valid_events]
            n = len(values)
            # Sort the values to compute the median. In a production system,
            # an approximation algorithm like t-digest could be used for performance.
            values.sort()
            if n % 2 == 1:
                median = values[n // 2]
            else:
                median = (values[n // 2 - 1] + values[n // 2]) / 2
            return median