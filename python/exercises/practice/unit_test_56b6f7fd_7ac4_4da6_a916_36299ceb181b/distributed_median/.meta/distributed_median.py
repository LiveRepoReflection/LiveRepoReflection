import heapq

class ShardMedian:
    def __init__(self):
        self.min_heap = []
        self.max_heap = []

    def insert(self, value):
        if not self.max_heap or value <= -self.max_heap[0]:
            heapq.heappush(self.max_heap, -value)
        else:
            heapq.heappush(self.min_heap, value)
        if len(self.max_heap) > len(self.min_heap) + 1:
            heapq.heappush(self.min_heap, -heapq.heappop(self.max_heap))
        elif len(self.min_heap) > len(self.max_heap):
            heapq.heappush(self.max_heap, -heapq.heappop(self.min_heap))

    def get_median(self):
        total_count = len(self.min_heap) + len(self.max_heap)
        if total_count == 0:
            raise ValueError("No data in shard")
        if total_count % 2 == 1:
            return float(-self.max_heap[0])
        else:
            return (float(-self.max_heap[0]) + float(self.min_heap[0])) / 2.0

class DistributedMedian:
    def __init__(self):
        self.shards = {}
        self.global_min_heap = []
        self.global_max_heap = []

    def ingest(self, shard, value):
        if shard not in self.shards:
            self.shards[shard] = ShardMedian()
        self.shards[shard].insert(value)
        if not self.global_max_heap or value <= -self.global_max_heap[0]:
            heapq.heappush(self.global_max_heap, -value)
        else:
            heapq.heappush(self.global_min_heap, value)
        if len(self.global_max_heap) > len(self.global_min_heap) + 1:
            heapq.heappush(self.global_min_heap, -heapq.heappop(self.global_max_heap))
        elif len(self.global_min_heap) > len(self.global_max_heap):
            heapq.heappush(self.global_max_heap, -heapq.heappop(self.global_min_heap))

    def get_local_median(self, shard):
        if shard not in self.shards or (len(self.shards[shard].min_heap) + len(self.shards[shard].max_heap)) == 0:
            raise ValueError("No data for local shard: " + shard)
        return self.shards[shard].get_median()

    def get_global_median(self):
        total_count = len(self.global_min_heap) + len(self.global_max_heap)
        if total_count == 0:
            raise ValueError("No data to compute global median")
        if total_count % 2 == 1:
            return float(-self.global_max_heap[0])
        else:
            return (float(-self.global_max_heap[0]) + float(self.global_min_heap[0])) / 2.0