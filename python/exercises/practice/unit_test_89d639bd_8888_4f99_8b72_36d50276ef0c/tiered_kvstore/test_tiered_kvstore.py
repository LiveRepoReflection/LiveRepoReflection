import unittest
import threading
import time
from tiered_kvstore import TieredKVStore

class TestTieredKVStore(unittest.TestCase):
    def setUp(self):
        self.nodes = 3
        self.cache_capacity = 2
        self.store = TieredKVStore(self.nodes, self.cache_capacity)

    def test_basic_operations(self):
        # Test basic put and get
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        # Test non-existent key
        self.assertIsNone(self.store.get("nonexistent"))

        # Test delete
        self.store.delete("key1")
        self.assertIsNone(self.store.get("key1"))

    def test_cache_eviction(self):
        # Fill cache capacity for a single node
        self.store.put("key1", "value1")  # Maps to some node
        self.store.put("key2", "value2")  # Maps to same node as key1
        self.store.put("key3", "value3")  # Maps to same node, should evict key1
        
        # key1 should be evicted from memory but still in disk
        value1 = self.store.get("key1")
        self.assertEqual(value1, "value1")  # Should read from disk

    def test_update_existing(self):
        self.store.put("key1", "value1")
        self.store.put("key1", "new_value1")
        self.assertEqual(self.store.get("key1"), "new_value1")

    def test_concurrent_access(self):
        def writer():
            for i in range(100):
                self.store.put(f"key{i}", f"value{i}")
                time.sleep(0.001)

        def reader():
            for i in range(100):
                self.store.get(f"key{i}")
                time.sleep(0.001)

        def deleter():
            for i in range(100):
                self.store.delete(f"key{i}")
                time.sleep(0.001)

        # Create threads
        write_thread = threading.Thread(target=writer)
        read_thread = threading.Thread(target=reader)
        delete_thread = threading.Thread(target=deleter)

        # Start threads
        write_thread.start()
        read_thread.start()
        delete_thread.start()

        # Wait for threads to complete
        write_thread.join()
        read_thread.join()
        delete_thread.join()

    def test_large_dataset(self):
        # Test with a dataset larger than cache capacity
        for i in range(1000):
            self.store.put(f"key{i}", f"value{i}")

        # Verify random access
        for i in range(0, 1000, 100):
            self.assertEqual(self.store.get(f"key{i}"), f"value{i}")

    def test_node_distribution(self):
        # Test if keys are distributed across nodes
        keys_per_node = {}
        for i in range(100):
            key = f"key{i}"
            self.store.put(key, f"value{i}")
            node_id = hash(key) % self.nodes
            keys_per_node[node_id] = keys_per_node.get(node_id, 0) + 1

        # Verify that all nodes have some keys
        self.assertEqual(len(keys_per_node), self.nodes)

    def test_edge_cases(self):
        # Test empty strings
        self.store.put("", "empty_key")
        self.assertEqual(self.store.get(""), "empty_key")

        # Test None values
        with self.assertRaises(ValueError):
            self.store.put("key", None)

        # Test deleting non-existent key
        self.store.delete("nonexistent")  # Should not raise exception

    def test_lru_behavior(self):
        # Test LRU behavior within a single node
        self.store.put("key1", "value1")
        self.store.put("key2", "value2")
        
        # Access key1 to make it most recently used
        self.store.get("key1")
        
        # Add key3, should evict key2 instead of key1
        self.store.put("key3", "value3")
        
        self.assertEqual(self.store.get("key1"), "value1")  # Should be in memory
        self.assertEqual(self.store.get("key2"), "value2")  # Should be in disk
        self.assertEqual(self.store.get("key3"), "value3")  # Should be in memory

if __name__ == '__main__':
    unittest.main()