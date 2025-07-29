import time
import threading
import heapq

class TimeCache:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()
        self.expiry_heap = []

    def put(self, key, value, ttl):
        current_time = time.time()
        expire_time = current_time + ttl if ttl > 0 else current_time - 1
        with self.lock:
            self.data[key] = (value, expire_time)
            heapq.heappush(self.expiry_heap, (expire_time, key))

    def get(self, key):
        current_time = time.time()
        with self.lock:
            if key not in self.data:
                return None
            value, expire_time = self.data[key]
            if expire_time <= current_time:
                # Entry has expired, remove it from data
                del self.data[key]
                return None
            return value

    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return True
            return False

    def size(self):
        with self.lock:
            return len(self.data)

    def evict_expired(self):
        current_time = time.time()
        with self.lock:
            while self.expiry_heap and self.expiry_heap[0][0] <= current_time:
                expire_time, key = heapq.heappop(self.expiry_heap)
                # Verify if the current entry in data matches the expired timestamp
                if key in self.data:
                    if self.data[key][1] <= current_time:
                        del self.data[key]