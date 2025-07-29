import threading
import time
import heapq
from collections import defaultdict
import sys


class EventStorage:
    """Storage mechanism for events with memory management"""
    
    def __init__(self, max_memory_mb):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.user_events = defaultdict(list)  # user_id -> [(timestamp, value), ...]
        self.total_events = 0
        self.event_size_bytes = 48  # Approximate size of a (timestamp, value) tuple in bytes
        self.lock = threading.RLock()
        
    def add_event(self, timestamp, user_id, value):
        """Add an event to the storage"""
        with self.lock:
            # Check memory usage before adding
            if self.estimate_memory_usage() >= self.max_memory_bytes:
                self._trim_storage()
            
            # Add the event
            self.user_events[user_id].append((timestamp, value))
            self.total_events += 1
            
            # Sort the events for this user by timestamp
            # In a more optimized implementation, we could use binary insertion instead
            self.user_events[user_id].sort(key=lambda x: x[0])
    
    def get_events_in_range(self, user_id, start_time, end_time):
        """Get all events for a user within a time range"""
        with self.lock:
            if user_id not in self.user_events:
                return []
            
            events = []
            for timestamp, value in self.user_events[user_id]:
                if start_time <= timestamp <= end_time:
                    events.append((timestamp, value))
            
            return events
    
    def estimate_memory_usage(self):
        """Estimate the current memory usage in bytes"""
        # Account for dictionary overhead
        overhead_per_user = 256  # Rough estimate
        
        # Calculate total bytes used
        total_bytes = (
            len(self.user_events) * overhead_per_user +  # User dictionary overhead
            self.total_events * self.event_size_bytes    # Event data
        )
        
        return total_bytes
    
    def _trim_storage(self):
        """Remove oldest events to free up memory"""
        # Strategy: remove 20% of oldest events across all users
        events_to_remove = max(1, self.total_events // 5)
        
        # Collect all events across all users with timestamps
        all_events = []
        for user_id, events in self.user_events.items():
            for timestamp, value in events:
                all_events.append((timestamp, user_id))
        
        # Sort by timestamp (oldest first)
        all_events.sort()
        
        # Determine cutoff timestamp
        if len(all_events) <= events_to_remove:
            # Clear everything if we need to remove everything
            self.user_events.clear()
            self.total_events = 0
            return
        
        cutoff_timestamp = all_events[events_to_remove - 1][0]
        
        # Remove all events with timestamp <= cutoff_timestamp
        events_removed = 0
        for user_id in list(self.user_events.keys()):
            original_count = len(self.user_events[user_id])
            self.user_events[user_id] = [
                (ts, val) for ts, val in self.user_events[user_id] 
                if ts > cutoff_timestamp
            ]
            removed = original_count - len(self.user_events[user_id])
            events_removed += removed
            
            # Remove empty user entries
            if not self.user_events[user_id]:
                del self.user_events[user_id]
        
        self.total_events -= events_removed


class EventAggregator:
    """
    A system for efficiently aggregating event streams in real-time.
    
    This implementation uses a memory-efficient event storage system
    with LRU-like trimming of old data when memory limits are reached.
    """
    
    def __init__(self, max_memory_mb=1000):
        """
        Initialize the EventAggregator with a specified memory limit.
        
        Args:
            max_memory_mb: Maximum memory usage in megabytes.
        """
        # Validate input
        if max_memory_mb <= 0:
            raise ValueError("Memory limit must be positive")
        
        self.storage = EventStorage(max_memory_mb)
        self.lock = threading.RLock()
    
    def ingest_event(self, timestamp, user_id, value):
        """
        Ingest a new event into the system.
        
        Args:
            timestamp: Event timestamp (milliseconds since epoch)
            user_id: User identifier
            value: Numerical value associated with the event
        """
        # Validate input
        if not isinstance(timestamp, (int, float)) or timestamp < 0:
            raise ValueError("Timestamp must be a non-negative number")
        
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a number")
        
        # Use integer timestamps only
        timestamp = int(timestamp)
        
        # Add the event to storage
        with self.lock:
            self.storage.add_event(timestamp, user_id, value)
    
    def aggregate_values(self, user_id, start_timestamp, end_timestamp):
        """
        Calculate the sum of all values for a user within the specified time window.
        
        Args:
            user_id: User identifier
            start_timestamp: Start of time window (inclusive)
            end_timestamp: End of time window (inclusive)
            
        Returns:
            The sum of values in the time window, or 0.0 if no data is available.
        """
        # Validate input
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        
        if not isinstance(start_timestamp, (int, float)) or start_timestamp < 0:
            raise ValueError("Start timestamp must be a non-negative number")
        
        if not isinstance(end_timestamp, (int, float)) or end_timestamp < 0:
            raise ValueError("End timestamp must be a non-negative number")
        
        # Use integer timestamps only
        start_timestamp = int(start_timestamp)
        end_timestamp = int(end_timestamp)
        
        # Handle invalid time range
        if start_timestamp > end_timestamp:
            return 0.0
        
        # Get events in the time range
        events = self.storage.get_events_in_range(user_id, start_timestamp, end_timestamp)
        
        # Calculate sum
        result = sum(value for _, value in events)
        
        return result


# Extended implementation with additional features

class AdvancedEventAggregator(EventAggregator):
    """
    Extended version of EventAggregator with additional aggregation functions
    and top-K user queries.
    """
    
    def aggregate_average(self, user_id, start_timestamp, end_timestamp):
        """Calculate the average value in the time window"""
        events = self.storage.get_events_in_range(user_id, start_timestamp, end_timestamp)
        if not events:
            return 0.0
        return sum(value for _, value in events) / len(events)
    
    def aggregate_min(self, user_id, start_timestamp, end_timestamp):
        """Calculate the minimum value in the time window"""
        events = self.storage.get_events_in_range(user_id, start_timestamp, end_timestamp)
        if not events:
            return None
        return min(value for _, value in events)
    
    def aggregate_max(self, user_id, start_timestamp, end_timestamp):
        """Calculate the maximum value in the time window"""
        events = self.storage.get_events_in_range(user_id, start_timestamp, end_timestamp)
        if not events:
            return None
        return max(value for _, value in events)
    
    def aggregate_stddev(self, user_id, start_timestamp, end_timestamp):
        """Calculate the standard deviation of values in the time window"""
        import math
        events = self.storage.get_events_in_range(user_id, start_timestamp, end_timestamp)
        if not events or len(events) < 2:
            return 0.0
        
        values = [value for _, value in events]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(variance)
    
    def get_top_users(self, start_timestamp, end_timestamp, k=10):
        """
        Get the top K users with highest aggregated values in the time window.
        
        Args:
            start_timestamp: Start of time window
            end_timestamp: End of time window
            k: Number of top users to return
            
        Returns:
            List of (user_id, sum_value) tuples, sorted by sum_value in descending order
        """
        with self.lock:
            user_sums = {}
            
            # Calculate sum for each user
            for user_id in self.storage.user_events.keys():
                events = self.storage.get_events_in_range(user_id, start_timestamp, end_timestamp)
                if events:
                    user_sums[user_id] = sum(value for _, value in events)
            
            # Get top K users
            top_users = heapq.nlargest(k, user_sums.items(), key=lambda x: x[1])
            
            return top_users


# Persistent version with disk storage

class PersistentEventAggregator(EventAggregator):
    """
    Version of EventAggregator with disk persistence for data recovery.
    """
    
    def __init__(self, max_memory_mb=1000, storage_file="event_data.dat"):
        """
        Initialize with memory limit and storage file.
        
        Args:
            max_memory_mb: Maximum memory usage in megabytes
            storage_file: Path to the file for persistent storage
        """
        super().__init__(max_memory_mb)
        self.storage_file = storage_file
        self.last_persist_time = time.time()
        self.persist_interval = 60  # seconds
        
        # Try to load existing data
        self._load_from_disk()
    
    def ingest_event(self, timestamp, user_id, value):
        """Override to add periodic persistence"""
        super().ingest_event(timestamp, user_id, value)
        
        # Check if it's time to persist
        current_time = time.time()
        if current_time - self.last_persist_time > self.persist_interval:
            self._persist_to_disk()
            self.last_persist_time = current_time
    
    def _persist_to_disk(self):
        """Save events to disk"""
        import pickle
        
        with self.lock:
            try:
                with open(self.storage_file, 'wb') as f:
                    pickle.dump(self.storage.user_events, f)
            except Exception as e:
                print(f"Error persisting data: {e}", file=sys.stderr)
    
    def _load_from_disk(self):
        """Load events from disk"""
        import pickle
        import os
        
        with self.lock:
            if not os.path.exists(self.storage_file):
                return
            
            try:
                with open(self.storage_file, 'rb') as f:
                    loaded_events = pickle.load(f)
                    
                    # Calculate total events
                    total = 0
                    for user_events in loaded_events.values():
                        total += len(user_events)
                    
                    self.storage.user_events = loaded_events
                    self.storage.total_events = total
                    
            except Exception as e:
                print(f"Error loading persisted data: {e}", file=sys.stderr)
    
    def force_persist(self):
        """Manually trigger persistence to disk"""
        self._persist_to_disk()
        self.last_persist_time = time.time()