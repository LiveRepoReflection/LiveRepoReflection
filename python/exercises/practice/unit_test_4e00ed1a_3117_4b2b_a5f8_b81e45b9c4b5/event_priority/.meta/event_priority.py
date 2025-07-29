import threading

class EventPrioritySystem:
    def __init__(self):
        self.events = {}
        self.lock = threading.Lock()

    def add_event(self, event_id, timestamp, priority, event_type):
        with self.lock:
            self.events[event_id] = {
                'event_id': event_id,
                'timestamp': timestamp,
                'priority': priority,
                'event_type': event_type
            }

    def remove_event(self, event_id):
        with self.lock:
            if event_id in self.events:
                del self.events[event_id]

    def get_top_k_events(self, k, start_time, end_time, event_types=None):
        with self.lock:
            filtered = []
            for event in self.events.values():
                if start_time <= event['timestamp'] <= end_time:
                    if event_types is None or event['event_type'] in event_types:
                        filtered.append(event)
            filtered.sort(key=lambda e: (-e['priority'], e['timestamp']))
            top_k = [e['event_id'] for e in filtered[:k]]
            return top_k