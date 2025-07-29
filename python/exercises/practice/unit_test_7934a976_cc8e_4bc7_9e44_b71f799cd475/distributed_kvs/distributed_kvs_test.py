import unittest
from distributed_kvs import DistributedKVS

class DistributedKVSTest(unittest.TestCase):
    def setUp(self):
        # Initialize with a set of nodes and a replication factor.
        self.initial_nodes = ["node1", "node2", "node3"]
        self.replication_factor = 2
        self.store = DistributedKVS(self.initial_nodes, self.replication_factor)

    def test_put_and_get(self):
        self.store.put("key1", "value1")
        result = self.store.get("key1")
        self.assertEqual(result, "value1", "Failed to get the correct value after put.")

    def test_overwrite_value(self):
        self.store.put("key2", "value2")
        self.assertEqual(self.store.get("key2"), "value2")
        # Overwrite the value.
        self.store.put("key2", "new_value2")
        self.assertEqual(self.store.get("key2"), "new_value2")

    def test_delete_key(self):
        self.store.put("key3", "value3")
        self.assertEqual(self.store.get("key3"), "value3")
        self.store.delete("key3")
        self.assertIsNone(self.store.get("key3"), "Deleted key should return None.")

    def test_get_nonexistent_key(self):
        self.assertIsNone(self.store.get("nonexistent"), "Non-existent key should return None.")

    def test_node_join(self):
        # Insert key before node join.
        self.store.put("key4", "value4")
        old_value = self.store.get("key4")
        self.assertEqual(old_value, "value4")
        # Simulate node join by adding a new node.
        new_nodes = self.initial_nodes + ["node4"]
        self.store.update_nodes(new_nodes)
        # Data should remain consistent after nodes change.
        self.assertEqual(self.store.get("key4"), "value4")

    def test_node_leave(self):
        # Insert key before node leave.
        self.store.put("key5", "value5")
        self.assertEqual(self.store.get("key5"), "value5")
        # Simulate node leave by removing one node.
        new_nodes = [node for node in self.initial_nodes if node != "node1"]
        self.store.update_nodes(new_nodes)
        # Data should remain available even after a node leaves.
        self.assertEqual(self.store.get("key5"), "value5")

    def test_multiple_keys_replication(self):
        # Insert multiple keys and verify that all keys are correctly replicated.
        keys = {f"key{i}": f"value{i}" for i in range(10)}
        for key, value in keys.items():
            self.store.put(key, value)
        for key, expected in keys.items():
            self.assertEqual(self.store.get(key), expected)

    def test_large_dataset(self):
        # Stress test with a large number of keys.
        num_keys = 1000
        for i in range(num_keys):
            key = f"large_key_{i}"
            value = f"large_value_{i}"
            self.store.put(key, value)
        for i in range(num_keys):
            key = f"large_key_{i}"
            value = f"large_value_{i}"
            self.assertEqual(self.store.get(key), value)

if __name__ == '__main__':
    unittest.main()