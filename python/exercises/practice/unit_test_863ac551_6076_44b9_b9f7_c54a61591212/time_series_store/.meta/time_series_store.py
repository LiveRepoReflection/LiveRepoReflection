import bisect
from collections import defaultdict

class TimeSeriesStore:
    def __init__(self):
        self.store = defaultdict(list)
        
    def set(self, key, value, timestamp):
        # Find insertion point to maintain sorted order
        timestamps = [t for t, v in self.store[key]]
        idx = bisect.bisect_right(timestamps, timestamp)
        # Check if timestamp already exists
        if idx > 0 and timestamps[idx-1] == timestamp:
            self.store[key][idx-1] = (timestamp, value)
        else:
            self.store[key].insert(idx, (timestamp, value))
    
    def get(self, key, timestamp):
        if key not in self.store or not self.store[key]:
            return -1
            
        timestamps = [t for t, v in self.store[key]]
        idx = bisect.bisect_right(timestamps, timestamp) - 1
        
        if idx >= 0:
            return self.store[key][idx][1]
        return -1
    
    def aggregate(self, key, startTime, endTime, aggregationType):
        if key not in self.store or not self.store[key]:
            if aggregationType in ["SUM", "AVG"]:
                return 0
            return -1
            
        timestamps = [t for t, v in self.store[key]]
        start_idx = bisect.bisect_left(timestamps, startTime)
        end_idx = bisect.bisect_right(timestamps, endTime)
        
        values_in_range = [v for t, v in self.store[key][start_idx:end_idx]]
        
        if not values_in_range:
            if aggregationType in ["SUM", "AVG"]:
                return 0
            return -1
            
        if aggregationType == "SUM":
            return sum(values_in_range)
        elif aggregationType == "AVG":
            return sum(values_in_range) / len(values_in_range)
        elif aggregationType == "MAX":
            return max(values_in_range)
        elif aggregationType == "MIN":
            return min(values_in_range)
        else:
            raise ValueError("Invalid aggregation type")