import unittest
import threading
import time
import random

from dist_kvstore import DistributedKVStore

class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        # Create a new instance of the distributed key-value store with a replication factor of 3
        self.store = DistributedKVStore(replication_factor=3)
        # Add initial nodes to the cluster
        for i in range(5):
            self.store.add_node("node" + str(i))
    
    def test_basic_put_get(self):
        # Test basic put and get operations
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1", "Basic get should return the value put.")

    def test_delete(self):
        # Test delete operation
        self.store.put("key2", "value2")
        self.store.delete("key2")
        self.assertIsNone(self.store.get("key2"), "Deleted key should return None.")

    def test_replication(self):
        # Test that value is still retrievable after a node failure due to replication
        self.store.put("key3", "value3")
        replicas = self.store.get_replicas("key3")
        # Simulate failure of one of the replica nodes
        failed_node = replicas[0]
        self.store.simulate_node_failure(failed_node)
        self.assertEqual(self.store.get("key3"), "value3", "Value should be retrievable after a node failure due to replication.")

    def test_node_join_leave(self):
        # Test the behavior when nodes join and leave the cluster
        self.store.put("key4", "value4")
        original_value = self.store.get("key4")
        
        # Node join
        new_node = "node_new"
        self.store.add_node(new_node)
        self.assertEqual(self.store.get("key4"), original_value, "Value should remain unchanged after a node joins.")

        # Node leave
        self.store.remove_node("node1")
        self.assertEqual(self.store.get("key4"), original_value, "Value should remain unchanged after a node leaves.")

    def test_consistency_after_writes(self):
        # Test consistency by concurrently writing different keys
        def writer(key, value):
            self.store.put(key, value)
        
        threads = []
        for i in range(20):
            t = threading.Thread(target=writer, args=("key{}".format(i), "value{}".format(i)))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

        for i in range(20):
            self.assertEqual(self.store.get("key{}".format(i)), "value{}".format(i),
                             "Concurrent write/read consistency check failed for key{}".format(i))

    def test_concurrent_reads_writes(self):
        # Simulate concurrent reads and writes on the same key
        key = "shared_key"
        
        def writer():
            for i in range(100):
                self.store.put(key, "val" + str(i))
                time.sleep(random.uniform(0.001, 0.005))
        
        def reader():
            for i in range(100):
                value = self.store.get(key)
                if value is not None:
                    self.assertTrue(value.startswith("val"), "Reader encountered unexpected value format.")
                time.sleep(random.uniform(0.001, 0.005))
        
        writer_threads = [threading.Thread(target=writer) for _ in range(3)]
        reader_threads = [threading.Thread(target=reader) for _ in range(3)]
        
        for t in writer_threads + reader_threads:
            t.start()
        for t in writer_threads + reader_threads:
            t.join()

    def test_multiple_valid_operations(self):
        # Test a sequence of put, update, and delete operations across multiple keys
        keys = ["alpha", "beta", "gamma", "delta"]
        values = ["A", "B", "C", "D"]
        for k, v in zip(keys, values):
            self.store.put(k, v)
        # Update one key and delete another
        self.store.put("gamma", "C_updated")
        self.store.delete("delta")
        self.assertEqual(self.store.get("gamma"), "C_updated", "Updated key should return the new value.")
        self.assertIsNone(self.store.get("delta"), "Deleted key should return None.")

    def test_simulated_failure_recovery(self):
        # Test that data remains retrievable after simulating multiple node failures
        self.store.put("resilient_key", "resilient_value")
        replicas = self.store.get_replicas("resilient_key")
        # Fail (replication_factor - 1) nodes
        for i in range(self.store.replication_factor - 1):
            self.store.simulate_node_failure(replicas[i])
        self.assertEqual(self.store.get("resilient_key"), "resilient_value",
                         "Value should be recoverable after multiple node failures.")

if __name__ == "__main__":
    unittest.main()