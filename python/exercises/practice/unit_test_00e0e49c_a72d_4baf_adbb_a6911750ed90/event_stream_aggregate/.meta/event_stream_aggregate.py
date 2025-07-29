from collections import defaultdict
import heapq
from typing import List, Tuple, Optional
import bisect

class TimeWindow:
    def __init__(self):
        self.timestamps = []  # Sorted list of timestamps
        self.values = []      # Values corresponding to timestamps
        self.total = 0.0      # Running total for quick access

    def add_event(self, timestamp: int, value: float) -> None:
        # Find the insertion point to maintain sorted order
        index = bisect.bisect_left(self.timestamps, timestamp)
        self.timestamps.insert(index, timestamp)
        self.values.insert(index, value)
        self.total += value

    def query_window(self, start_ts: int, end_ts: int) -> Tuple[float, int]:
        """Returns (sum, count) for events within the time window."""
        start_idx = bisect.bisect_left(self.timestamps, start_ts)
        end_idx = bisect.bisect_right(self.timestamps, end_ts)
        
        if start_idx == end_idx:
            return 0.0, 0
        
        window_sum = sum(self.values[start_idx:end_idx])
        return window_sum, end_idx - start_idx

    def cleanup_old_events(self, cutoff_ts: int) -> None:
        """Removes events older than cutoff_ts."""
        if not self.timestamps:
            return
            
        cutoff_idx = bisect.bisect_left(self.timestamps, cutoff_ts)
        if cutoff_idx > 0:
            self.total -= sum(self.values[:cutoff_idx])
            self.timestamps = self.timestamps[cutoff_idx:]
            self.values = self.values[cutoff_idx:]

class EventStreamAggregator:
    def __init__(self, cleanup_window: int = 24 * 60 * 60 * 1000):  # Default 24 hour cleanup
        self.events = defaultdict(TimeWindow)  # event_type -> TimeWindow
        self.cleanup_window = cleanup_window
        self.latest_timestamp = 0

    def process_event(self, timestamp: int, event_type: str, value: float) -> None:
        """Process an incoming event."""
        self.events[event_type].add_event(timestamp, value)
        self.latest_timestamp = max(self.latest_timestamp, timestamp)
        
        # Cleanup old events periodically
        if timestamp - self.cleanup_window > self.latest_timestamp - 2 * self.cleanup_window:
            self._cleanup_old_events(timestamp - self.cleanup_window)

    def handle_query(self, query_type: str, start_timestamp: int, end_timestamp: int, 
                    event_type: Optional[str] = None, K: Optional[int] = None) -> float:
        """Handle different types of queries."""
        if query_type == "total":
            return self._handle_total_query(start_timestamp, end_timestamp, event_type)
        elif query_type == "average":
            return self._handle_average_query(start_timestamp, end_timestamp, event_type)
        elif query_type == "topk":
            return self._handle_topk_query(start_timestamp, end_timestamp, K)
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def _handle_total_query(self, start_ts: int, end_ts: int, event_type: str) -> float:
        """Handle a total query for a specific event type."""
        if event_type not in self.events:
            return 0.0
        total, _ = self.events[event_type].query_window(start_ts, end_ts)
        return total

    def _handle_average_query(self, start_ts: int, end_ts: int, event_type: str) -> float:
        """Handle an average query for a specific event type."""
        if event_type not in self.events:
            return 0.0
        total, count = self.events[event_type].query_window(start_ts, end_ts)
        return total / count if count > 0 else 0.0

    def _handle_topk_query(self, start_ts: int, end_ts: int, K: int) -> List[Tuple[str, float]]:
        """Handle a top-K query across all event types."""
        event_totals = []
        for event_type, window in self.events.items():
            total, _ = window.query_window(start_ts, end_ts)
            if total > 0:  # Only include non-zero totals
                event_totals.append((-total, event_type))  # Negative for max-heap behavior
        
        # Use heapq to get top K elements
        heapq.heapify(event_totals)
        result = []
        while event_totals and len(result) < K:
            neg_total, event_type = heapq.heappop(event_totals)
            result.append((event_type, -neg_total))
        
        return result

    def _cleanup_old_events(self, cutoff_ts: int) -> None:
        """Clean up events older than the cutoff timestamp."""
        for window in self.events.values():
            window.cleanup_old_events(cutoff_ts)