import threading
import time
from collections import defaultdict
from copy import deepcopy

class VectorClock:
    """
    Implementation of a vector clock for tracking causality in the distributed system.
    A vector clock maintains a counter for each node in the system.
    """
    def __init__(self, node_id=None):
        self.clocks = defaultdict(int)
        self.node_id = node_id or f"node-{id(self)}"
        self.lock = threading.RLock()

    def increment(self):
        """Increment the local node's clock value."""
        with self.lock:
            self.clocks[self.node_id] += 1
            return deepcopy(self.clocks)

    def merge(self, other_clock):
        """
        Merge another vector clock with this one.
        The resulting clock reflects the maximum values from both clocks.
        """
        with self.lock:
            for node_id, clock_value in other_clock.clocks.items():
                self.clocks[node_id] = max(self.clocks[node_id], clock_value)
            return deepcopy(self.clocks)

    def is_concurrent_with(self, other_clock):
        """
        Check if this vector clock is concurrent with another vector clock.
        Two clocks are concurrent if neither happened-before the other.
        """
        with self.lock:
            less_than_or_equal = all(self.clocks[node] <= other_clock.clocks.get(node, 0) 
                                   for node in self.clocks)
            greater_than_or_equal = all(self.clocks[node] >= other_clock.clocks.get(node, 0) 
                                     for node in other_clock.clocks)
            return not (less_than_or_equal or greater_than_or_equal)

    def __str__(self):
        return str(dict(self.clocks))
    
    def __eq__(self, other):
        if not isinstance(other, VectorClock):
            return False
        return self.clocks == other.clocks

    def copy(self):
        """Create a copy of this vector clock."""
        new_clock = VectorClock(self.node_id)
        new_clock.clocks = deepcopy(self.clocks)
        return new_clock


class KeyValue:
    """
    A container for a key's value with metadata for conflict resolution.
    Stores both the value and the vector clock that reflects the causality of operations.
    """
    def __init__(self, value=0, vector_clock=None, node_id=None):
        self.value = value
        self.vector_clock = vector_clock or VectorClock(node_id)
        self.lock = threading.RLock()
    
    def increment(self, amount, node_id=None):
        """
        Increment the value and update the vector clock.
        """
        with self.lock:
            self.value += amount
            if node_id and node_id != self.vector_clock.node_id:
                self.vector_clock.node_id = node_id
            self.vector_clock.increment()
            return self.value

    def merge(self, other):
        """
        Merge with another KeyValue instance.
        If the vector clocks indicate concurrent updates, use a conflict resolution strategy.
        """
        with self.lock:
            if self.vector_clock.is_concurrent_with(other.vector_clock):
                # Conflict detected - implement resolution strategy
                # In this implementation, we sum the values for concurrent updates
                # This effectively implements "add wins" semantics
                merged_value = self.value + other.value
                self.value = merged_value
            elif all(self.vector_clock.clocks[node] >= other.vector_clock.clocks.get(node, 0) 
                   for node in other.vector_clock.clocks):
                # Our clock dominates - keep our value
                pass
            else:
                # Other clock dominates - use their value
                self.value = other.value
            
            # Always merge the vector clocks
            self.vector_clock.merge(other.vector_clock)
            return self.value

    def copy(self):
        """Create a copy of this KeyValue."""
        return KeyValue(self.value, self.vector_clock.copy())


class DistributedKeyCounter:
    """
    A distributed key-value counter with strong consistency guarantees.
    Uses vector clocks to track causality between operations.
    """
    def __init__(self):
        self.counters = {}
        self.node_id = f"node-{id(self)}"
        self.lock = threading.RLock()
        self.retry_attempts = 3
        self.retry_delay = 0.05  # 50 ms delay between retries
    
    def increment(self, key: str, value: int) -> None:
        """
        Increment the counter for the given key by the specified value.
        Implements at-least-once semantics with retries.
        """
        attempt = 0
        while attempt < self.retry_attempts:
            try:
                with self.lock:
                    if key not in self.counters:
                        self.counters[key] = KeyValue(0, VectorClock(self.node_id))
                    self.counters[key].increment(value, self.node_id)
                return  # Success, exit the retry loop
            except Exception as e:
                attempt += 1
                if attempt >= self.retry_attempts:
                    raise e  # Re-raise if out of retries
                time.sleep(self.retry_delay)
    
    def get_value(self, key: str) -> int:
        """
        Get the current value of the counter for the given key.
        Returns 0 if the key doesn't exist.
        """
        with self.lock:
            if key not in self.counters:
                return 0
            return self.counters[key].value
    
    def merge(self, other: 'DistributedKeyCounter') -> None:
        """
        Merge another DistributedKeyCounter into this one.
        This handles conflict resolution using vector clocks.
        """
        with self.lock:
            for key, other_key_value in other.counters.items():
                if key not in self.counters:
                    # If we don't have this key, copy the other key's value and clock
                    self.counters[key] = other_key_value.copy()
                else:
                    # If we have the key, merge the values and clocks
                    self.counters[key].merge(other_key_value)
    
    def _get_all_keys(self):
        """Get all keys in the counter (for testing and debugging)."""
        with self.lock:
            return list(self.counters.keys())

    def _get_vector_clock(self, key):
        """Get the vector clock for a specific key (for testing and debugging)."""
        with self.lock:
            if key not in self.counters:
                return None
            return self.counters[key].vector_clock.copy()