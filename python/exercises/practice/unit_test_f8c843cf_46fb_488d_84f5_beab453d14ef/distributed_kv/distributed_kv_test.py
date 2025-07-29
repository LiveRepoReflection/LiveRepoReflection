import unittest
from distributed_kv import DistributedKVStore

class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        # Initialize the distributed key-value store with 5 nodes and replication factor 3.
        self.num_nodes = 5
        self.replication_factor = 3
        self.store = DistributedKVStore(num_nodes=self.num_nodes, replication_factor=self.replication_factor)

    def _compute_primary(self, key):
        # Consistent hashing: for simplicity, assume key converts to int if possible,
        # otherwise use the absolute value of the built-in hash and mod with number of nodes.
        try:
            k = int(key)
        except ValueError:
            k = abs(hash(key))
        return k % self.num_nodes

    def test_put_and_get(self):
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")

    def test_put_and_remove(self):
        self.store.put("key2", "value2")
        self.assertEqual(self.store.get("key2"), "value2")
        self.store.remove("key2")
        self.assertIsNone(self.store.get("key2"))

    def test_replication_fallback(self):
        # Insert a key-value pair and simulate failure of its primary node.
        self.store.put("key3", "value3")
        primary = self._compute_primary("key3")
        self.store.node_failure(primary)
        # The value should still be retrievable from one of its replicas.
        self.assertEqual(self.store.get("key3"), "value3")
        # Recover the primary and verify consistent retrieval.
        self.store.recover_node(primary)
        self.assertEqual(self.store.get("key3"), "value3")

    def test_node_failure_multiple(self):
        # Insert multiple key-value pairs.
        keys = ["a", "b", "c", "d"]
        for key in keys:
            self.store.put(key, f"value_{key}")
        # Simulate failures in two different nodes.
        self.store.node_failure(0)
        self.store.node_failure(1)
        for key in keys:
            self.assertEqual(self.store.get(key), f"value_{key}")
        # Recover one node and check retrieval again.
        self.store.recover_node(0)
        for key in keys:
            self.assertEqual(self.store.get(key), f"value_{key}")

    def test_recover_node(self):
        # Test that a node recovery correctly reintegrates its data.
        self.store.put("key4", "value4")
        primary = self._compute_primary("key4")
        self.store.node_failure(primary)
        self.assertEqual(self.store.get("key4"), "value4")
        self.store.recover_node(primary)
        self.assertEqual(self.store.get("key4"), "value4")

    def test_non_existent_key(self):
        # Requesting a key that was never added should return None.
        self.assertIsNone(self.store.get("nonexistent"))

    def test_overwrite_value(self):
        # If a key already exists, putting a new value overwrites the old value.
        self.store.put("key5", "value5")
        self.assertEqual(self.store.get("key5"), "value5")
        self.store.put("key5", "value5_new")
        self.assertEqual(self.store.get("key5"), "value5_new")

    def test_consistent_hashing_distribution(self):
        # Insert multiple keys to test that each can be retrieved correctly,
        # which indirectly verifies the distribution mechanism.
        keys = [str(i) for i in range(20)]
        for key in keys:
            self.store.put(key, f"value_{key}")
        for key in keys:
            self.assertEqual(self.store.get(key), f"value_{key}")

if __name__ == '__main__':
    unittest.main()