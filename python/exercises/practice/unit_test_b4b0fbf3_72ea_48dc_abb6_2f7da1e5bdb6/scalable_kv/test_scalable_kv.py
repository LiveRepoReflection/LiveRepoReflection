import unittest
from typing import List, Tuple, Optional
import random
import time

class TestScalableKVStore(unittest.TestCase):
    def setUp(self):
        from scalable_kv import KVStore
        self.store = KVStore()

    def test_basic_put_get(self):
        self.store.put(1000, b"value1")
        self.assertEqual(self.store.get(1000), b"value1")

    def test_nonexistent_key(self):
        self.assertIsNone(self.store.get(999999))

    def test_update_existing_key(self):
        self.store.put(2000, b"original")
        self.store.put(2000, b"updated")
        self.assertEqual(self.store.get(2000), b"updated")

    def test_range_query_empty(self):
        result = self.store.range_query(5000, 6000)
        self.assertEqual(len(result), 0)

    def test_range_query_single_result(self):
        self.store.put(3000, b"alone")
        result = self.store.range_query(2999, 3001)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (3000, b"alone"))

    def test_range_query_multiple_results(self):
        test_data = [(1000, b"a"), (2000, b"b"), (3000, b"c")]
        for k, v in test_data:
            self.store.put(k, v)
        
        result = self.store.range_query(999, 3001)
        self.assertEqual(len(result), 3)
        self.assertEqual(sorted(result), test_data)

    def test_range_query_partial_overlap(self):
        test_data = [(1000, b"a"), (2000, b"b"), (3000, b"c")]
        for k, v in test_data:
            self.store.put(k, v)
        
        result = self.store.range_query(1500, 2500)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (2000, b"b"))

    def test_large_dataset(self):
        # Generate 10000 random entries
        test_data = [(i * 1000, str(i).encode()) for i in range(10000)]
        random.shuffle(test_data)
        
        # Insert data
        start_time = time.time()
        for k, v in test_data:
            self.store.put(k, v)
        insert_time = time.time() - start_time
        
        # Test point queries
        start_time = time.time()
        for k, v in random.sample(test_data, 1000):
            result = self.store.get(k)
            self.assertEqual(result, v)
        point_query_time = time.time() - start_time
        
        # Test range queries
        start_time = time.time()
        for _ in range(100):
            start = random.randint(0, 9000000)
            end = start + random.randint(1000, 100000)
            result = self.store.range_query(start, end)
            # Verify results are sorted and within range
            self.assertTrue(all(start <= k <= end for k, _ in result))
            self.assertTrue(all(k1 <= k2 for (k1, _), (k2, _) in zip(result, result[1:])))
        range_query_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(insert_time, 2.0)  # 2 seconds for 10K inserts
        self.assertLess(point_query_time, 1.0)  # 1 second for 1K queries
        self.assertLess(range_query_time, 5.0)  # 5 seconds for 100 range queries

    def test_out_of_order_inserts(self):
        # Test handling of out-of-order insertions
        timestamps = [
            (1000000, b"latest"),
            (999000, b"older"),
            (999500, b"middle"),
        ]
        random.shuffle(timestamps)
        
        for ts, value in timestamps:
            self.store.put(ts, value)
        
        result = self.store.range_query(999000, 1000000)
        self.assertEqual(len(result), 3)
        self.assertEqual([k for k, _ in result], [999000, 999500, 1000000])

    def test_data_locality(self):
        # Insert data with some gaps
        base_time = int(time.time() * 1e9)  # Current time in nanoseconds
        for i in range(0, 1000, 10):
            self.store.put(base_time + i, str(i).encode())
        
        # Insert data in between
        for i in range(5, 1000, 10):
            self.store.put(base_time + i, str(i).encode())
        
        # Verify range query performance
        start_time = time.time()
        result = self.store.range_query(base_time, base_time + 1000)
        query_time = time.time() - start_time
        
        self.assertEqual(len(result), 200)  # Should have 200 entries
        self.assertLess(query_time, 0.1)  # Should be fast due to data locality

    def test_large_values(self):
        # Test with values approaching the 1KB limit
        large_value = b"x" * 1024
        self.store.put(1000, large_value)
        self.assertEqual(self.store.get(1000), large_value)

    def test_consistency(self):
        # Test read-your-writes consistency
        ops = [
            (2000, b"first"),
            (2000, b"second"),
            (2000, b"third")
        ]
        
        for ts, value in ops:
            self.store.put(ts, value)
            result = self.store.get(ts)
            self.assertEqual(result, value)

if __name__ == '__main__':
    unittest.main()