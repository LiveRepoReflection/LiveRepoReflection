import threading
import queue
import math
import heapq

class SlidingWindow:
    def __init__(self, window_size):
        self.window_size = window_size
        self.current_size = 0
        # Running statistics: count, sum, and sum of squares.
        self.count = 0
        self.total = 0.0
        self.total_sq = 0.0
        # Two heaps for median maintenance.
        self.max_heap = []  # Max heap (invert values to simulate max heap)
        self.min_heap = []  # Min heap
        # Lazy deletion dictionaries for each heap.
        self.del_max = {}
        self.del_min = {}

    def add(self, value):
        # Update running statistics.
        self.count += 1
        self.total += value
        self.total_sq += value * value
        self.current_size += 1

        # Add to appropriate heap.
        if not self.max_heap or value <= -self.max_heap[0]:
            heapq.heappush(self.max_heap, -value)
        else:
            heapq.heappush(self.min_heap, value)
        self._rebalance()

    def remove(self, value):
        # Update running statistics.
        self.count -= 1
        self.total -= value
        self.total_sq -= value * value
        self.current_size -= 1

        # Determine which heap the value likely belongs to.
        # Use current median as pivot.
        median = self.get_median() if self.current_size > 0 else value
        if value <= median:
            # Mark value for lazy deletion in max_heap.
            self.del_max[-value] = self.del_max.get(-value, 0) + 1
            # If the value is at top, remove it.
            if self.max_heap and -self.max_heap[0] == value:
                self._prune(self.max_heap, self.del_max)
        else:
            self.del_min[value] = self.del_min.get(value, 0) + 1
            if self.min_heap and self.min_heap[0] == value:
                self._prune(self.min_heap, self.del_min)
        self._rebalance()

    def _rebalance(self):
        # Balance sizes of the two heaps. The difference cannot exceed 1.
        if len(self.max_heap) > len(self.min_heap) + 1:
            self._prune(self.max_heap, self.del_max)
            val = -heapq.heappop(self.max_heap)
            heapq.heappush(self.min_heap, val)
        elif len(self.min_heap) > len(self.max_heap):
            self._prune(self.min_heap, self.del_min)
            val = heapq.heappop(self.min_heap)
            heapq.heappush(self.max_heap, -val)
        # Clean up tops.
        self._prune(self.max_heap, self.del_max)
        self._prune(self.min_heap, self.del_min)

    def _prune(self, heap, del_dict):
        # Remove elements from top of heap that are marked for deletion.
        while heap and del_dict.get(heap[0] if heap is self.min_heap else -heap[0], 0):
            key = heap[0] if heap is self.min_heap else -heap[0]
            heapq.heappop(heap)
            if del_dict[key] == 1:
                del del_dict[key]
            else:
                del_dict[key] -= 1

    def get_median(self):
        # Ensure heaps are cleaned up.
        self._prune(self.max_heap, self.del_max)
        self._prune(self.min_heap, self.del_min)
        if not self.max_heap and not self.min_heap:
            return 0.0
        if len(self.max_heap) > len(self.min_heap):
            return -self.max_heap[0]
        else:
            return (-self.max_heap[0] + self.min_heap[0]) / 2.0

    def get_mean(self):
        if self.count == 0:
            return 0.0
        return self.total / self.count

    def get_variance(self):
        if self.count == 0:
            return 0.0
        mean = self.get_mean()
        # Variance = E[x^2] - (E[x])^2
        variance = (self.total_sq / self.count) - (mean * mean)
        # Avoid floating point negative zeros.
        return variance if variance > 0 else 0.0

class StreamProcessor:
    def __init__(self, window_size, k_threshold):
        self.window_size = window_size
        self.k_threshold = k_threshold
        self.window = SlidingWindow(window_size)
        self.event_queue = queue.Queue(maxsize=window_size * 2)
        self.anomalies = []
        self.buffer = []  # To store events in order for sliding window removals.
        self.lock = threading.Lock()
        self.worker_thread = threading.Thread(target=self._process)
        self.worker_thread.start()

    def _process(self):
        while True:
            item = self.event_queue.get()
            if item is None:  # Sentinel to signal end of stream.
                break
            timestamp, value = item
            with self.lock:
                # If current window is full, evict the oldest event.
                if len(self.buffer) >= self.window_size:
                    old_timestamp, old_value = self.buffer.pop(0)
                    self.window.remove(old_value)
                # Add the current event.
                self.buffer.append((timestamp, value))
                self.window.add(value)
                # Compute current statistics.
                mean = self.window.get_mean()
                variance = self.window.get_variance()
                std = math.sqrt(variance)
                # Check for anomaly.
                # If std is zero, no deviation can be computed; skip anomaly detection.
                if std > 0 and abs(value - mean) > self.k_threshold * std:
                    self.anomalies.append((timestamp, value))
            self.event_queue.task_done()

    def add_event(self, event):
        self.event_queue.put(event)

    def finish(self):
        # Signal termination and wait for worker thread.
        self.event_queue.put(None)
        self.worker_thread.join()

def process_stream(event_iterator, window_size, k_threshold):
    """
    Process the event stream to detect anomalies.
    Each event is a tuple (timestamp, value).
    Returns a list of anomalies (timestamp, value) in the order they are detected.
    """
    processor = StreamProcessor(window_size, k_threshold)
    for event in event_iterator:
        processor.add_event(event)
    processor.event_queue.join()  # Wait for all events to be processed.
    processor.finish()
    return processor.anomalies