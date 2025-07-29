import heapq
import threading
from collections import defaultdict, deque
import bisect

class DistributedAggregator:
    def __init__(self, k: int, window_size: int):
        """
        Initialize the distributed aggregator with the k-th value to find and the time window size.
        
        Args:
            k (int): The k-th smallest value to find (1 <= k <= 100)
            window_size (int): The time window size in seconds (1 <= window_size <= 600)
        """
        self.k = k
        self.window_size = window_size
        
        # Store metrics data: {metric_name: [(timestamp, value), ...]}
        self.metrics = defaultdict(list)
        
        # Maintain sorted values for efficient k-th smallest calculation: {metric_name: sorted_values}
        self.sorted_values = defaultdict(list)
        
        # Keep track of current time (latest timestamp seen)
        self.current_time = 0
        
        # Thread safety lock
        self.lock = threading.RLock()
    
    def process_event(self, event: dict):
        """
        Process an event from a worker node.
        
        Args:
            event (dict): The event to process with structure:
                {
                    "timestamp": int,
                    "worker_id": str,
                    "metric_name": str,
                    "metric_value": float
                }
        """
        timestamp = event["timestamp"]
        metric_name = event["metric_name"]
        metric_value = event["metric_value"]
        
        with self.lock:
            # Update current time if this event has a newer timestamp
            self.current_time = max(self.current_time, timestamp)
            
            # Add the event to the metrics data
            self.metrics[metric_name].append((timestamp, metric_value))
            
            # Update the sorted values (insert in sorted position)
            bisect.insort(self.sorted_values[metric_name], metric_value)
            
            # Clean up expired events
            self._cleanup_expired_events(metric_name)
    
    def get_kth_smallest(self, metric_name: str) -> float:
        """
        Get the k-th smallest value for a given metric within the current time window.
        
        Args:
            metric_name (str): The name of the metric
        
        Returns:
            float: The k-th smallest value, or -1 if there are fewer than k values
        """
        with self.lock:
            # Clean up any expired events first
            self._cleanup_expired_events(metric_name)
            
            # Check if we have enough values
            if metric_name not in self.sorted_values or len(self.sorted_values[metric_name]) < self.k:
                return -1
            
            # Return the k-th smallest value (0-indexed, so k-1)
            return self.sorted_values[metric_name][self.k - 1]
    
    def _cleanup_expired_events(self, metric_name: str):
        """
        Remove events that have fallen outside the current time window.
        
        Args:
            metric_name (str): The metric name to clean up
        """
        if metric_name not in self.metrics:
            return
            
        # Calculate the cutoff time for the window
        cutoff_time = self.current_time - self.window_size
        
        # Find the index of the first non-expired event
        events = self.metrics[metric_name]
        valid_start_idx = 0
        while valid_start_idx < len(events) and events[valid_start_idx][0] <= cutoff_time:
            # Remove the expired value from sorted values
            expired_value = events[valid_start_idx][1]
            
            # Find and remove the value from sorted list
            idx = bisect.bisect_left(self.sorted_values[metric_name], expired_value)
            if idx < len(self.sorted_values[metric_name]) and self.sorted_values[metric_name][idx] == expired_value:
                self.sorted_values[metric_name].pop(idx)
                
            valid_start_idx += 1
        
        # Remove expired events
        if valid_start_idx > 0:
            self.metrics[metric_name] = events[valid_start_idx:]