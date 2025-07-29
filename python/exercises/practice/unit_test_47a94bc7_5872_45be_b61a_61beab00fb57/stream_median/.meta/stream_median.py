import heapq

class MedianFinder:
    def __init__(self):
        self.max_heap = []  # stores the smaller half (max at root)
        self.min_heap = []  # stores the larger half (min at root)
        
    def add_number(self, num):
        if not self.max_heap or num <= -self.max_heap[0]:
            heapq.heappush(self.max_heap, -num)
        else:
            heapq.heappush(self.min_heap, num)
            
        self._balance_heaps()
        
    def _balance_heaps(self):
        if len(self.max_heap) > len(self.min_heap) + 1:
            moved_num = -heapq.heappop(self.max_heap)
            heapq.heappush(self.min_heap, moved_num)
        elif len(self.min_heap) > len(self.max_heap):
            moved_num = heapq.heappop(self.min_heap)
            heapq.heappush(self.max_heap, -moved_num)
            
    def get_median(self):
        if not self.max_heap and not self.min_heap:
            raise ValueError("No numbers added yet")
            
        if len(self.max_heap) == len(self.min_heap):
            return (-self.max_heap[0] + self.min_heap[0]) / 2
        else:
            return float(-self.max_heap[0])