from collections import defaultdict, deque
from datetime import datetime
import threading
from typing import List, Dict, Set, Deque

class LogAggregator:
    def __init__(self, num_services: int, keywords: List[str], window_seconds: int):
        """Initialize the LogAggregator with given parameters."""
        self.num_services = num_services
        self.keywords = set(keyword.lower() for keyword in keywords)
        self.window_seconds = window_seconds
        
        # Storage for logs per service
        self.logs: Dict[int, List[tuple[datetime, str]]] = defaultdict(list)
        
        # Sliding window implementation for keyword counting
        self.keyword_counts: Dict[str, int] = defaultdict(int)
        self.keyword_timestamps: Dict[str, Deque[datetime]] = {
            keyword: deque() for keyword in self.keywords
        }
        
        # Thread safety
        self.lock = threading.Lock()

    def _validate_service_id(self, service_id: int) -> None:
        """Validate the service ID is within acceptable range."""
        if not 0 <= service_id < self.num_services:
            raise ValueError(f"Invalid service ID: {service_id}")

    def _validate_time_range(self, start_time: datetime, end_time: datetime) -> None:
        """Validate the time range is logical."""
        if start_time > end_time:
            raise ValueError("Start time must be before end time")

    def _clean_old_keyword_counts(self, current_time: datetime) -> None:
        """Remove keyword counts that are outside the sliding window."""
        cutoff_time = current_time.timestamp() - self.window_seconds
        
        for keyword in self.keywords:
            while (self.keyword_timestamps[keyword] and 
                  self.keyword_timestamps[keyword][0].timestamp() < cutoff_time):
                self.keyword_timestamps[keyword].popleft()
                self.keyword_counts[keyword] -= 1

    def _update_keyword_counts(self, message: str, timestamp: datetime) -> None:
        """Update the count of keywords in the current window."""
        message_lower = message.lower()
        for keyword in self.keywords:
            if keyword in message_lower:
                self.keyword_counts[keyword] += 1
                self.keyword_timestamps[keyword].append(timestamp)

    def ingest_log(self, service_id: int, message: str, timestamp: datetime) -> None:
        """Ingest a new log entry."""
        self._validate_service_id(service_id)
        
        with self.lock:
            # Store the log
            self.logs[service_id].append((timestamp, message))
            
            # Update keyword counts
            self._update_keyword_counts(message, timestamp)
            self._clean_old_keyword_counts(timestamp)
            
            # Sort logs by timestamp (optimization: could be done periodically instead)
            self.logs[service_id].sort(key=lambda x: x[0])

    def get_logs(self, service_id: int, start_time: datetime, end_time: datetime) -> List[str]:
        """Retrieve logs for a specific service within a time range."""
        self._validate_service_id(service_id)
        self._validate_time_range(start_time, end_time)
        
        with self.lock:
            # Binary search for start index
            logs = self.logs[service_id]
            start_idx = self._binary_search(logs, start_time)
            end_idx = self._binary_search(logs, end_time)
            
            # Return all logs within the time range
            return [msg for ts, msg in logs[start_idx:end_idx+1]
                   if start_time <= ts <= end_time]

    def _binary_search(self, logs: List[tuple[datetime, str]], target_time: datetime) -> int:
        """Binary search for the closest log entry to target_time."""
        if not logs:
            return 0
            
        left, right = 0, len(logs) - 1
        
        while left < right:
            mid = (left + right) // 2
            if logs[mid][0] < target_time:
                left = mid + 1
            else:
                right = mid
                
        return left

    def get_keyword_count(self, keyword: str) -> int:
        """Get the current count of a keyword within the sliding window."""
        keyword = keyword.lower()
        if keyword not in self.keywords:
            return 0
            
        with self.lock:
            current_time = datetime.now()
            self._clean_old_keyword_counts(current_time)
            return self.keyword_counts[keyword]
