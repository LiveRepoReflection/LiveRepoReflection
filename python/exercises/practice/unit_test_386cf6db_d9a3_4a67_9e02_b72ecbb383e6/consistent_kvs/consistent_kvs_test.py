import unittest
import threading
import time
from consistent_kvs import DistributedKeyValueStore

class TestDistributedKeyValueStore(unittest.TestCase):
    def setUp(self):
        # Initialize distributed key-value store with 3 nodes,
        # replication factor = 2, and a ring size of 1024.
        self.store = DistributedKeyValueStore(initial_nodes=3, replication_factor=2, ring_size=1024)

    def test_put_and_get(self):
        # Basic put and get operation.
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")

    def test_overwrite_value(self):
        # Last write wins: update the same key twice.
        self.store.put("key_overwrite", "first")
        time.sleep(0.01)  # Ensure distinct timestamp if applicable
        self.store.put("key_overwrite", "second")
        self.assertEqual(self.store.get("key_overwrite"), "second")

    def test_empty_key_and_value(self):
        # Test handling of empty key and empty value.
        # Depending on the implementation, empty key might be stored as a valid key.
        self.store.put("", "non_empty")
        self.assertEqual(self.store.get(""), "non_empty")
        self.store.put("empty_value", "")
        self.assertEqual(self.store.get("empty_value"), "")

    def test_nonexistent_key(self):
        # Attempt to retrieve a key that doesn't exist.
        self.assertIsNone(self.store.get("nonexistent"))

    def test_node_join(self):
        # Test behavior when a new node joins the cluster.
        # Add some keys and then add a node.
        self.store.put("join_key1", "value1")
        self.store.put("join_key2", "value2")
        old_value = self.store.get("join_key1")
        self.store.add_node()  # Dynamically add a new node
        # After rebalancing, the key should still be retrievable.
        self.assertEqual(self.store.get("join_key1"), old_value)
        self.assertEqual(self.store.get("join_key2"), "value2")

    def test_node_leave(self):
        # Test behavior when a node leaves the cluster.
        self.store.put("leave_key1", "value1")
        self.store.put("leave_key2", "value2")
        # Remove one node.
        self.store.remove_node()
        # Data should be rebalanced across the remaining nodes.
        self.assertEqual(self.store.get("leave_key1"), "value1")
        self.assertEqual(self.store.get("leave_key2"), "value2")

    def test_replication(self):
        # Test that replication factor is honored.
        self.store.put("replicate_key", "replicate_value")
        # Simulate failure of one replica by removing a node that holds the key.
        # For testing, remove a node, then check if the key is still available.
        self.store.remove_node()
        self.assertEqual(self.store.get("replicate_key"), "replicate_value")

    def test_concurrent_put_get(self):
        # Test concurrent put and get operations.
        def put_values(start, end):
            for i in range(start, end):
                self.store.put(f"concurrent_key_{i}", f"value_{i}")

        def get_values(start, end, results):
            for i in range(start, end):
                results[i] = self.store.get(f"concurrent_key_{i}")

        thread_count = 5
        keys_per_thread = 20
        threads = []
        for t in range(thread_count):
            start = t * keys_per_thread
            end = (t + 1) * keys_per_thread
            thread = threading.Thread(target=put_values, args=(start, end))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # Now concurrently read values.
        results = {}
        threads = []
        for t in range(thread_count):
            start = t * keys_per_thread
            end = (t + 1) * keys_per_thread
            thread = threading.Thread(target=get_values, args=(start, end, results))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        
        # Verify all keys
        for i in range(thread_count * keys_per_thread):
            self.assertEqual(results.get(i), f"value_{i}")

if __name__ == '__main__':
    unittest.main()