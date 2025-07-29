import unittest
import threading
import time

from keyval_store.store import KeyValStore

class TestKeyValStore(unittest.TestCase):
    def setUp(self):
        # Initialize a distributed key-value store with 5 nodes and a replication factor of 3.
        self.store = KeyValStore(num_nodes=5, replication_factor=3)

    def test_basic_put_get(self):
        self.store.put("apple", "red")
        result = self.store.get("apple")
        self.assertEqual(result, "red")

    def test_missing_key(self):
        result = self.store.get("nonexistent")
        self.assertIsNone(result)

    def test_overwrite_latest_wins(self):
        # Write an initial value, then update it after a brief delay to simulate a later timestamp.
        self.store.put("banana", "yellow")
        time.sleep(0.01)
        self.store.put("banana", "ripe yellow")
        result = self.store.get("banana")
        self.assertEqual(result, "ripe yellow")

    def test_node_failure_handling(self):
        # Put several key-value pairs to set up the store.
        keys = ["key1", "key2", "key3"]
        values = ["value1", "value2", "value3"]
        for key, value in zip(keys, values):
            self.store.put(key, value)

        # Simulate node failure on one of the nodes (assuming node IDs from 0 to num_nodes-1).
        failed_node = 2
        self.store.crash_node(failed_node)

        # Perform additional writes and reads to verify the store remains operational.
        self.store.put("key4", "value4")
        self.assertEqual(self.store.get("key1"), "value1")
        self.assertEqual(self.store.get("key4"), "value4")

        # Recover the failed node and test that the data is consistent across replicas.
        self.store.recover_node(failed_node)
        self.assertEqual(self.store.get("key2"), "value2")

    def worker_put(self, key, value):
        self.store.put(key, value)

    def test_concurrent_puts(self):
        # Test concurrent writes to the same key. The last write should win.
        num_threads = 10
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=self.worker_put, args=("concurrent_key", f"value_{i}"))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        result = self.store.get("concurrent_key")
        expected_values = [f"value_{i}" for i in range(num_threads)]
        self.assertIn(result, expected_values)

    def test_concurrent_gets_and_puts(self):
        # Test concurrent read and write operations on multiple keys.
        def putter(key, value):
            for _ in range(5):
                self.store.put(key, value)
                time.sleep(0.005)

        def getter(key, results):
            for _ in range(5):
                res = self.store.get(key)
                results.append(res)
                time.sleep(0.005)

        keys = [f"key{i}" for i in range(5)]
        writer_threads = []
        reader_threads = []
        results_dict = {key: [] for key in keys}

        for key in keys:
            t_put = threading.Thread(target=putter, args=(key, key + "_value"))
            t_get = threading.Thread(target=getter, args=(key, results_dict[key]))
            writer_threads.append(t_put)
            reader_threads.append(t_get)

        for t in writer_threads:
            t.start()
        for t in reader_threads:
            t.start()

        for t in writer_threads:
            t.join()
        for t in reader_threads:
            t.join()

        # Verify that at least one of the get operations returned the expected value.
        for key in keys:
            self.assertTrue(any(val == key + "_value" for val in results_dict[key]),
                            f"Expected value {key + '_value'} not found for key {key}.")

if __name__ == "__main__":
    unittest.main()