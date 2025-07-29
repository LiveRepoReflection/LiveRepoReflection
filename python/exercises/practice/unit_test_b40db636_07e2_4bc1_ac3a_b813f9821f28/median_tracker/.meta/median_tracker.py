import heapq

class MedianTracker:
    def __init__(self):
        # min_heap: stores the larger half as (price, unique_id)
        self.min_heap = []
        # max_heap: stores the smaller half as (-price, unique_id)
        self.max_heap = []
        # Mapping from data center id to set of unique ids for prices reported
        self.data_centers = {}
        # Global unique counter for each reported price
        self.unique_counter = 0
        # Mapping from unique_id to tuple: (price, heap_type) where heap_type is "max" or "min"
        self.entry_info = {}
        # Set of unique ids that have been removed (lazy deletion)
        self.invalid_ids = set()
        # These counts reflect the number of valid entries in each heap
        self.count_max = 0
        self.count_min = 0

    def add_data_center(self, data_center_id):
        if data_center_id in self.data_centers:
            # Already exists, do nothing or optionally raise error if duplicates are not allowed.
            return
        self.data_centers[data_center_id] = set()

    def report_price(self, data_center_id, price):
        if data_center_id not in self.data_centers:
            raise ValueError(f"Data center {data_center_id} has not been added.")
        uid = self.unique_counter
        self.unique_counter += 1
        # Decide where to put the new price.
        # If no valid elements exist in the max_heap, push to max_heap.
        self._prune_heap(self.max_heap, True)
        if self.count_max == 0:
            # No elements in lower half, so add here.
            heapq.heappush(self.max_heap, (-price, uid))
            self.entry_info[uid] = (price, "max")
            self.count_max += 1
        else:
            # Get current median from max_heap
            median = -self.max_heap[0][0]
            if price <= median:
                heapq.heappush(self.max_heap, (-price, uid))
                self.entry_info[uid] = (price, "max")
                self.count_max += 1
            else:
                heapq.heappush(self.min_heap, (price, uid))
                self.entry_info[uid] = (price, "min")
                self.count_min += 1
        # Add unique id to corresponding data center record
        self.data_centers[data_center_id].add(uid)
        # Rebalance to ensure the difference is at most one
        self._rebalance_heaps()

    def remove_data_center(self, data_center_id):
        if data_center_id not in self.data_centers:
            # If non-existent, do nothing.
            return
        # Mark all prices from this data center as invalid.
        for uid in self.data_centers[data_center_id]:
            if uid in self.invalid_ids:
                continue
            self.invalid_ids.add(uid)
            # Update the count based on which heap it belongs to.
            if uid in self.entry_info:
                _, heap_type = self.entry_info[uid]
                if heap_type == "max":
                    self.count_max -= 1
                else:
                    self.count_min -= 1
        # Remove the data center record.
        del self.data_centers[data_center_id]
        # Clean up the tops of heaps and rebalance.
        self._prune_heap(self.max_heap, True)
        self._prune_heap(self.min_heap, False)
        self._rebalance_heaps()

    def get_global_median(self):
        # Clean up the heaps first.
        self._prune_heap(self.max_heap, True)
        self._prune_heap(self.min_heap, False)
        total_valid = self.count_max + self.count_min
        if total_valid == 0:
            return -1
        # The median is defined as the top of max_heap (lower middle in even case)
        self._rebalance_heaps()
        self._prune_heap(self.max_heap, True)
        if self.max_heap:
            median = -self.max_heap[0][0]
            return median
        return -1

    def _prune_heap(self, heap, is_max):
        # Remove elements from the top of the heap that are marked invalid.
        while heap and heap[0][1] in self.invalid_ids:
            heapq.heappop(heap)
            if is_max:
                # The count has been decremented in remove_data_center already.
                # We ensure consistency if any lazy invalid remains at top.
                pass
            else:
                pass

    def _rebalance_heaps(self):
        # Ensure that the max_heap has either the same amount or one more than min_heap.
        self._prune_heap(self.max_heap, True)
        self._prune_heap(self.min_heap, False)
        # While max_heap has more than one extra valid entry than min_heap, move one element from max_heap to min_heap.
        while self.count_max > self.count_min + 1:
            self._prune_heap(self.max_heap, True)
            if not self.max_heap:
                break
            neg_price, uid = heapq.heappop(self.max_heap)
            self.count_max -= 1
            price = -neg_price
            heapq.heappush(self.min_heap, (price, uid))
            self.entry_info[uid] = (price, "min")
            self.count_min += 1
            self._prune_heap(self.max_heap, True)
            self._prune_heap(self.min_heap, False)
        # If min_heap has more valid entries than max_heap, move one element from min_heap to max_heap.
        while self.count_min > self.count_max:
            self._prune_heap(self.min_heap, False)
            if not self.min_heap:
                break
            price, uid = heapq.heappop(self.min_heap)
            self.count_min -= 1
            heapq.heappush(self.max_heap, (-price, uid))
            self.entry_info[uid] = (price, "max")
            self.count_max += 1
            self._prune_heap(self.min_heap, False)
            self._prune_heap(self.max_heap, True)