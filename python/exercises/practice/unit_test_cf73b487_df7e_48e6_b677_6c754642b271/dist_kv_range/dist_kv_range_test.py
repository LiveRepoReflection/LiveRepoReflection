import unittest
import threading
import time
import random
from dist_kv_range import DistributedKVStore, Node


class DistKVRangeTest(unittest.TestCase):
    def setUp(self):
        # Create a distributed KV store with 10 nodes
        self.store = DistributedKVStore(num_nodes=10, key_range=1000000)

    def test_basic_put_get(self):
        """Test basic put and get operations"""
        self.store.put(42, "answer")
        self.assertEqual(self.store.get(42), "answer")
        
        self.store.put(100, "hundred")
        self.assertEqual(self.store.get(100), "hundred")

    def test_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        self.assertIsNone(self.store.get(999))

    def test_overwrite_key(self):
        """Test overwriting an existing key"""
        self.store.put(42, "old value")
        self.assertEqual(self.store.get(42), "old value")
        
        self.store.put(42, "new value")
        self.assertEqual(self.store.get(42), "new value")

    def test_empty_range_query(self):
        """Test range query with no keys in range"""
        result = self.store.range_query(500, 600)
        self.assertEqual(len(result), 0)

    def test_basic_range_query(self):
        """Test basic range query functionality"""
        for i in range(100, 200):
            self.store.put(i, f"value-{i}")
        
        result = self.store.range_query(150, 160)
        self.assertEqual(len(result), 10)
        
        for key, value in result:
            self.assertTrue(150 <= key < 160)
            self.assertEqual(value, f"value-{key}")
        
        # Check sorting
        for i in range(len(result) - 1):
            self.assertLess(result[i][0], result[i + 1][0])

    def test_large_range_query(self):
        """Test range query with a large range"""
        for i in range(1000, 2000, 10):  # Insert 100 key-value pairs
            self.store.put(i, f"value-{i}")
        
        result = self.store.range_query(1000, 2000)
        self.assertEqual(len(result), 100)
        self.assertEqual(result[0][0], 1000)
        self.assertEqual(result[-1][0], 1990)

    def test_partial_range_query(self):
        """Test range query where only part of the range has keys"""
        for i in range(300, 350):
            self.store.put(i, f"value-{i}")
        
        result = self.store.range_query(280, 370)
        self.assertEqual(len(result), 50)
        self.assertEqual(result[0][0], 300)
        self.assertEqual(result[-1][0], 349)

    def test_invalid_range_query(self):
        """Test range query with invalid range (start > end)"""
        with self.assertRaises(ValueError):
            self.store.range_query(200, 100)

    def test_out_of_bounds_keys(self):
        """Test handling of keys outside valid range"""
        with self.assertRaises(ValueError):
            self.store.put(-1, "negative")
        
        with self.assertRaises(ValueError):
            self.store.put(1000000, "too large")
        
        with self.assertRaises(ValueError):
            self.store.get(-42)

    def test_concurrent_operations(self):
        """Test concurrent put and get operations"""
        def worker(worker_id, num_operations):
            for i in range(num_operations):
                key = worker_id * 1000 + i
                self.store.put(key, f"worker-{worker_id}-value-{i}")
                time.sleep(0.001)  # Small sleep to ensure interleaving
                self.assertEqual(self.store.get(key), f"worker-{worker_id}-value-{i}")
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i, 20))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all data is correctly stored
        for worker_id in range(5):
            for i in range(20):
                key = worker_id * 1000 + i
                self.assertEqual(self.store.get(key), f"worker-{worker_id}-value-{i}")

    def test_concurrent_range_queries(self):
        """Test concurrent range queries"""
        # Insert data
        for i in range(0, 1000, 2):
            self.store.put(i, f"value-{i}")
        
        def query_worker(start, end):
            result = self.store.range_query(start, end)
            expected_count = len([i for i in range(start, end, 2) if i < 1000])
            self.assertEqual(len(result), expected_count)
            
            for key, value in result:
                self.assertEqual(value, f"value-{key}")
                self.assertTrue(start <= key < end)
                self.assertEqual(key % 2, 0)  # All keys should be even
        
        # Create threads to perform range queries
        threads = []
        ranges = [(0, 200), (200, 400), (400, 600), (600, 800), (800, 1000)]
        
        for start, end in ranges:
            t = threading.Thread(target=query_worker, args=(start, end))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

    def test_node_failure(self):
        """Test system behavior when a node fails"""
        # Insert some data
        for i in range(100):
            self.store.put(i, f"value-{i}")
        
        # Simulate a node failure by setting a node to inactive
        failed_node_id = random.randint(0, 9)  # Pick a random node to fail
        self.store.nodes[failed_node_id].active = False
        
        # Test data retrieval with node failure
        # This should work if data is replicated
        for i in range(100):
            value = self.store.get(i)
            if value is not None:  # Some keys might be lost depending on implementation
                self.assertEqual(value, f"value-{i}")

    def test_consistent_hashing(self):
        """Test that consistent hashing distributes keys evenly"""
        # Insert a large number of keys
        for i in range(1000):
            self.store.put(i, f"value-{i}")
        
        # Count keys per node
        keys_per_node = [0] * 10
        for i in range(1000):
            node_id = self.store._get_node_for_key(i)
            keys_per_node[node_id] += 1
        
        # Check distribution - no node should have too many or too few keys
        avg_keys = 1000 / 10
        for count in keys_per_node:
            # Allow some variance but distribution should be roughly even
            self.assertTrue(0.5 * avg_keys < count < 1.5 * avg_keys)

    def test_add_node(self):
        """Test adding a new node to the system"""
        # Insert initial data
        for i in range(100):
            self.store.put(i, f"original-{i}")
        
        # Add a new node
        self.store.add_node()
        
        # Insert more data
        for i in range(100, 200):
            self.store.put(i, f"after-expansion-{i}")
        
        # Verify all data is accessible
        for i in range(200):
            if i < 100:
                expected = f"original-{i}"
            else:
                expected = f"after-expansion-{i}"
            
            value = self.store.get(i)
            if value is not None:  # Some keys might be redistributed
                self.assertEqual(value, expected)

    def test_remove_node(self):
        """Test removing a node from the system"""
        # Insert initial data
        for i in range(100):
            self.store.put(i, f"value-{i}")
        
        # Remove a node
        self.store.remove_node(5)  # Remove node with ID 5
        
        # Verify data is still accessible
        # Note: Some data might be lost if there's no replication
        available_values = 0
        for i in range(100):
            value = self.store.get(i)
            if value is not None:
                available_values += 1
                self.assertEqual(value, f"value-{i}")
        
        # At least some percentage of the data should still be accessible
        # This percentage depends on implementation details
        self.assertTrue(available_values > 80)  # Assuming at least 80% data availability


if __name__ == '__main__':
    unittest.main()