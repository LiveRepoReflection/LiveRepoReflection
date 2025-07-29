from bisect import insort, bisect_left, bisect_right

class EventAggregator:
    def __init__(self):
        # Dictionary mapping metric name to a sorted list of tuples (timestamp, metric_value)
        self.data = {}

    def ingest_event(self, event):
        metric = event["metric_name"]
        ts = event["timestamp"]
        value = event["metric_value"]

        if metric not in self.data:
            self.data[metric] = []
        # Insert the event in sorted order by timestamp
        insort(self.data[metric], (ts, value))

    def query(self, metric_name, time_window_start, time_window_end):
        if metric_name not in self.data:
            events = []
        else:
            events = self.data[metric_name]

        # Locate left and right indices using bisect for efficient querying
        left_idx = bisect_left(events, (time_window_start, float('-inf')))
        right_idx = bisect_right(events, (time_window_end, float('inf')))
        selected = events[left_idx:right_idx]

        count = len(selected)
        total = sum(val for ts, val in selected) if selected else 0.0
        avg = total / count if count else None
        if selected:
            min_val = min(val for ts, val in selected)
            max_val = max(val for ts, val in selected)
        else:
            min_val = None
            max_val = None

        return {
            "metric_name": metric_name,
            "time_window_start": time_window_start,
            "time_window_end": time_window_end,
            "count": count,
            "sum": total,
            "avg": avg,
            "min": min_val,
            "max": max_val
        }