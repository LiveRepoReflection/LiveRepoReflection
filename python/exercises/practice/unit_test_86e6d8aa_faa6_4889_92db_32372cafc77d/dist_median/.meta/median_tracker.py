import heapq
from collections import defaultdict

class MedianTracker:
    def __init__(self):
        self.node_data = defaultdict(list)
        self.global_min_heap = []
        self.global_max_heap = []
        self.total_count = 0
        
    def add_value(self, node_id, value):
        # Store value in node's local storage
        self.node_data[node_id].append(value)
        self.total_count += 1
        
        # Periodically update global heaps (simulating network communication)
        if len(self.node_data[node_id]) % 100 == 0:
            self._update_global_stats(node_id)
    
    def _update_global_stats(self, node_id):
        # Get node's local data
        local_data = sorted(self.node_data[node_id])
        n = len(local_data)
        
        # Calculate node's approximate quantiles
        q1 = local_data[n//4] if n >= 4 else local_data[0]
        median = local_data[n//2] if n >= 2 else local_data[0]
        q3 = local_data[3*n//4] if n >= 4 else local_data[-1]
        
        # Update global heaps
        heapq.heappush(self.global_max_heap, -q1)
        heapq.heappush(self.global_min_heap, q3)
        
        # Maintain heap balance
        if len(self.global_max_heap) > len(self.global_min_heap) + 1:
            heapq.heappush(self.global_min_heap, -heapq.heappop(self.global_max_heap))
        elif len(self.global_min_heap) > len(self.global_max_heap):
            heapq.heappush(self.global_max_heap, -heapq.heappop(self.global_min_heap))
    
    def estimate_median(self):
        if self.total_count == 0:
            raise ValueError("No data available to compute median")
            
        # If we have enough global data, use it
        if self.global_max_heap and self.global_min_heap:
            if len(self.global_max_heap) == len(self.global_min_heap):
                return (-self.global_max_heap[0] + self.global_min_heap[0]) / 2
            else:
                return -self.global_max_heap[0]
        
        # Fallback: combine all node medians (expensive, simulate network aggregation)
        all_medians = []
        for node_id in self.node_data:
            local_data = sorted(self.node_data[node_id])
            n = len(local_data)
            if n > 0:
                median = local_data[n//2] if n >= 2 else local_data[0]
                all_medians.append(median)
        
        if not all_medians:
            raise ValueError("No data available to compute median")
            
        all_medians.sort()
        n = len(all_medians)
        if n % 2 == 1:
            return all_medians[n//2]
        else:
            return (all_medians[n//2 - 1] + all_medians[n//2]) / 2