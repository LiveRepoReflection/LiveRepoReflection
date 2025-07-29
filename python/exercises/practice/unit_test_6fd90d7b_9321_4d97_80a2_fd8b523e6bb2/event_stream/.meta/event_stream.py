from collections import defaultdict
import bisect

class EventStreamAggregator:
    def __init__(self):
        # Data structure: 
        # {
        #   event_type: {
        #       entity_id: [(timestamp, value), ...]
        #   }
        # }
        self.event_data = defaultdict(lambda: defaultdict(list))
        # Secondary index for timestamps
        self.timestamp_index = defaultdict(list)

    def process_event(self, timestamp, entity_id, event_type, value):
        """Process an incoming event and store it in the appropriate data structures."""
        # Store event in primary data structure
        bisect.insort(self.event_data[event_type][entity_id], (timestamp, value))
        # Update timestamp index
        bisect.insort(self.timestamp_index[event_type], timestamp)

    def query(self, start_time, end_time, entity_ids, event_type):
        """Query the sum of values for matching events within the specified parameters."""
        total = 0
        
        # Check if event type exists
        if event_type not in self.event_data:
            return 0
            
        # Optimize by checking timestamp range first
        timestamps = self.timestamp_index.get(event_type, [])
        if not timestamps:
            return 0
            
        # Binary search to find the valid time range
        left = bisect.bisect_left(timestamps, start_time)
        right = bisect.bisect_right(timestamps, end_time)
        
        # If no events in time range
        if left == right:
            return 0
            
        # Process each requested entity
        for entity_id in entity_ids:
            if entity_id not in self.event_data[event_type]:
                continue
                
            # Get all events for this entity and event type
            events = self.event_data[event_type][entity_id]
            
            # Binary search to find the first event >= start_time
            left_idx = bisect.bisect_left(events, (start_time,))
            # Binary search to find the first event > end_time
            right_idx = bisect.bisect_right(events, (end_time, float('inf')))
            
            # Sum all values in the range
            for i in range(left_idx, right_idx):
                total += events[i][1]
                
        return total

    def get_all_events(self):
        """Helper method for testing - returns all stored events in timestamp order."""
        all_events = []
        for event_type, entities in self.event_data.items():
            for entity_id, events in entities.items():
                for timestamp, value in events:
                    all_events.append((timestamp, entity_id, event_type, value))
        return sorted(all_events, key=lambda x: x[0])