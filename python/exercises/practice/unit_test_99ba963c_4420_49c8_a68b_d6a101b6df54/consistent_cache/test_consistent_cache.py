import unittest
import threading
import time
from typing import Optional, Tuple

class TestConsistentCache(unittest.TestCase):
    def setUp(self):
        # Import here to ensure clean slate for each test
        from consistent_cache import DistributedCache
        self.cache = DistributedCache(n_nodes=3, replication_factor=2, node_capacity=100)

    def test_basic_put_get(self):
        self.cache.put("key1", "value1", 1)
        value, timestamp = self.cache.get("key1")
        self.assertEqual(value, "value1")
        self.assertEqual(timestamp, 1)

    def test_update_with_newer_timestamp(self):
        self.cache.put("key1", "value1", 1)
        self.cache.put("key1", "value2", 2)
        value, timestamp = self.cache.get("key1")
        self.assertEqual(value, "value2")
        self.assertEqual(timestamp, 2)

    def test_update_with_older_timestamp(self):
        self.cache.put("key1", "value2", 2)
        self.cache.put("key1", "value1", 1)
        value, timestamp = self.cache.get("key1")
        self.assertEqual(value, "value2")
        self.assertEqual(timestamp, 2)

    def test_remove(self):
        self.cache.put("key1", "value1", 1)
        self.cache.remove("key1", 2)
        value, timestamp = self.cache.get("key1")
        self.assertEqual(value, None)
        self.assertEqual(timestamp, -1)

    def test_remove_with_older_timestamp(self):
        self.cache.put("key1", "value1", 2)
        self.cache.remove("key1", 1)
        value, timestamp = self.cache.get("key1")
        self.assertEqual(value, "value1")
        self.assertEqual(timestamp, 2)

    def test_nonexistent_key(self):
        value, timestamp = self.cache.get("nonexistent")
        self.assertEqual(value, None)
        self.assertEqual(timestamp, -1)

    def test_cache_eviction(self):
        # Fill cache to capacity
        for i in range(200):  # More than node capacity
            self.cache.put(f"key{i}", f"value{i}", i)
        
        # Check that some early items were evicted
        value, timestamp = self.cache.get("key0")
        self.assertEqual(value, None)
        self.assertEqual(timestamp, -1)

    def test_concurrent_access(self):
        def writer():
            for i in range(100):
                self.cache.put(f"concurrent_key{i}", f"value{i}", i)

        def reader():
            for i in range(100):
                self.cache.get(f"concurrent_key{i}")

        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=writer))
            threads.append(threading.Thread(target=reader))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def test_node_failure_recovery(self):
        # Put some data
        self.cache.put("key1", "value1", 1)
        
        # Simulate node failure by removing a node
        failed_node_id = 0
        original_nodes = self.cache._nodes.copy()
        self.cache._nodes.pop(failed_node_id)

        # Should still be able to get data due to replication
        value, timestamp = self.cache.get("key1")
        self.assertEqual(value, "value1")

        # Restore node
        self.cache._nodes[failed_node_id] = original_nodes[failed_node_id]

        # Data should still be accessible
        value, timestamp = self.cache.get("key1")
        self.assertEqual(value, "value1")

    def test_consistent_hashing(self):
        # Put same key multiple times
        for i in range(10):
            self.cache.put("stable_key", f"value{i}", i)
        
        # Get the nodes responsible for this key
        key_hash = hash("stable_key")
        responsible_nodes = []
        for node_id in self.cache._nodes:
            if self.cache._is_node_responsible(node_id, key_hash):
                responsible_nodes.append(node_id)
        
        # Should have exactly R nodes responsible
        self.assertEqual(len(responsible_nodes), self.cache._replication_factor)

    def test_large_values(self):
        large_value = "x" * 100000  # 100KB string
        self.cache.put("large_key", large_value, 1)
        value, timestamp = self.cache.get("large_key")
        self.assertEqual(value, large_value)

if __name__ == '__main__':
    unittest.main()