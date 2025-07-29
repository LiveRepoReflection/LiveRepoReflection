import unittest
import threading
import time
from dist_key_value import KeyValueStore

class TestDistributedKeyValueStore(unittest.TestCase):
    def setUp(self):
        # Initialize a distributed key-value store with 5 nodes and replication factor of 3.
        self.store = KeyValueStore(num_nodes=5, replication_factor=3)

    def test_put_and_get(self):
        self.store.put("key1", "value1")
        result = self.store.get("key1")
        self.assertEqual(result, "value1", "Basic put/get operation failed.")

    def test_get_non_existent_key(self):
        result = self.store.get("nonexistent")
        self.assertIsNone(result, "Getting a nonexistent key should return None.")

    def test_delete(self):
        self.store.put("key_del", "to_delete")
        self.assertEqual(self.store.get("key_del"), "to_delete", "Value not found after put.")
        self.store.delete("key_del")
        result = self.store.get("key_del")
        self.assertIsNone(result, "Deleted key should not return a value.")

    def test_conflict_resolution(self):
        # Test that the last write wins using version numbers.
        self.store.put("key_conflict", "initial")
        time.sleep(0.01)  # Ensure a timestamp difference
        self.store.put("key_conflict", "updated")
        result = self.store.get("key_conflict")
        self.assertEqual(result, "updated", "Conflict resolution (last write wins) failed.")

    def test_replication_under_node_failure(self):
        # Put a key, force one replica to be unavailable, then get should still return the correct value.
        self.store.put("key_rep", "replicated")
        # Simulate node failure: mark node with id 1 as unavailable.
        self.store.set_node_availability(1, False)
        result = self.store.get("key_rep")
        self.assertEqual(result, "replicated", "Replication across nodes failed when a node is unavailable.")
        self.store.set_node_availability(1, True)

    def test_eventual_consistency(self):
        # Update a key and assume eventual consistency mechanism will propagate the latest version
        self.store.put("key_eventual", "v1")
        self.store.put("key_eventual", "v2")
        time.sleep(0.05)  # Allow time for consistency to propagate
        result = self.store.get("key_eventual")
        self.assertEqual(result, "v2", "Eventual consistency failed to converge to the latest update.")

    def test_concurrent_access(self):
        # Test thread safety by concurrently performing put and get operations.
        def put_values(prefix, start, count):
            for i in range(start, start + count):
                key = f"{prefix}_{i}"
                self.store.put(key, f"value_{i}")
                time.sleep(0.001)

        def get_values(prefix, start, count, results):
            for i in range(start, start + count):
                key = f"{prefix}_{i}"
                value = self.store.get(key)
                results.append((key, value))
                time.sleep(0.001)

        threads = []
        results = []
        # Start concurrent writers
        for j in range(5):
            t = threading.Thread(target=put_values, args=("concurrent", j * 10, 10))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        # Start concurrent readers
        threads = []
        for j in range(5):
            t = threading.Thread(target=get_values, args=("concurrent", j * 10, 10, results))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        # Verify every key has been written and can be read.
        for key, value in results:
            self.assertIsNotNone(value, f"Concurrent get failed for key {key}.")

    def test_delete_propagation(self):
        # Test that a deletion marker eventually removes the key from all replicas.
        self.store.put("key_del_consistent", "value_del")
        # Simulate a node failure on one replica.
        self.store.set_node_availability(2, False)
        self.store.delete("key_del_consistent")
        # Restore the node and allow for consistency synchronization.
        self.store.set_node_availability(2, True)
        time.sleep(0.05)
        result = self.store.get("key_del_consistent")
        self.assertIsNone(result, "Deletion did not propagate across all replicas.")

    def test_hinted_handoff(self):
        # Simulate a node failure during a put and validate that hinted handoff works when node comes back online.
        self.store.set_node_availability(3, False)
        self.store.put("key_handoff", "hinted")
        # Bring the failed node back online.
        self.store.set_node_availability(3, True)
        time.sleep(0.05)  # Wait for background synchronization of hinted data.
        result = self.store.get("key_handoff")
        self.assertEqual(result, "hinted", "Hinted handoff failed to recover the data after node failure.")

if __name__ == '__main__':
    unittest.main()