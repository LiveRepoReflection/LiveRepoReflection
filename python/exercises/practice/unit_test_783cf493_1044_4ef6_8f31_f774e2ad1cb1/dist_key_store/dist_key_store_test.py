import unittest
import threading
import time

from dist_key_store import Client, Node

class DummyNode(Node):
    def __init__(self, address):
        super().__init__(address)
        self.data_store = {}
        self.healthy = True

    def put(self, key, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        # Last-write wins: update only if the new timestamp is greater or key does not exist.
        if key not in self.data_store or self.data_store[key][1] <= timestamp:
            self.data_store[key] = (value, timestamp)

    def get(self, key):
        return self.data_store.get(key, (None, None))[0]

    def delete(self, key):
        if key in self.data_store:
            del self.data_store[key]

    def health_check(self):
        return self.healthy

class DummyClient(Client):
    def __init__(self, nodes, replication_factor=2):
        self.nodes = nodes
        self.replication_factor = replication_factor

    def _get_nodes_for_key(self, key):
        # Simple deterministic selection based on sum of ASCII codes modulo number of nodes.
        index = sum(ord(c) for c in key) % len(self.nodes)
        selected = []
        for i in range(self.replication_factor):
            selected.append(self.nodes[(index + i) % len(self.nodes)])
        return selected

    def put(self, key, value):
        timestamp = time.time()
        nodes = self._get_nodes_for_key(key)
        for node in nodes:
            node.put(key, value, timestamp)

    def get(self, key):
        nodes = self._get_nodes_for_key(key)
        val, ts = None, -1
        for node in nodes:
            if node.health_check():
                local_value, local_ts = node.data_store.get(key, (None, -1))
                if local_ts > ts:
                    ts = local_ts
                    val = local_value
        return val

    def delete(self, key):
        nodes = self._get_nodes_for_key(key)
        for node in nodes:
            node.delete(key)

    def health_check(self):
        return all(node.health_check() for node in self.nodes)

class TestDistKeyStore(unittest.TestCase):
    def setUp(self):
        self.node1 = DummyNode("node1")
        self.node2 = DummyNode("node2")
        self.node3 = DummyNode("node3")
        self.nodes = [self.node1, self.node2, self.node3]
        self.client = DummyClient(self.nodes, replication_factor=2)

    def test_health_check_all_healthy(self):
        self.assertTrue(self.client.health_check())

    def test_put_and_get(self):
        key = "file1.txt"
        value = b"metadata1"
        self.client.put(key, value)
        retrieved = self.client.get(key)
        self.assertEqual(retrieved, value)

    def test_get_nonexistent_key(self):
        self.assertIsNone(self.client.get("nonexistent.txt"))

    def test_delete_key(self):
        key = "file2.txt"
        value = b"metadata2"
        self.client.put(key, value)
        self.client.delete(key)
        self.assertIsNone(self.client.get(key))

    def test_replication(self):
        key = "file3.txt"
        value = b"metadata3"
        self.client.put(key, value)
        nodes_for_key = self.client._get_nodes_for_key(key)
        count = sum(1 for node in self.nodes if key in node.data_store)
        self.assertEqual(count, self.client.replication_factor)
        for node in nodes_for_key:
            self.assertEqual(node.get(key), value)

    def test_conflict_resolution_last_write_wins(self):
        key = "file4.txt"
        first_value = b"metadata_first"
        second_value = b"metadata_second"
        nodes_for_key = self.client._get_nodes_for_key(key)
        old_ts = time.time() - 10
        for node in nodes_for_key:
            node.put(key, first_value, old_ts)
        self.client.put(key, second_value)
        retrieved = self.client.get(key)
        self.assertEqual(retrieved, second_value)

    def test_concurrent_puts(self):
        key = "file5.txt"
        values = [b"value1", b"value2", b"value3", b"value4", b"value5"]

        def put_value(val):
            self.client.put(key, val)

        threads = []
        for v in values:
            t = threading.Thread(target=put_value, args=(v,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        retrieved = self.client.get(key)
        self.assertIn(retrieved, values)

    def test_large_data_transfer(self):
        key = "large_file.bin"
        value = bytes(1024 * 1024)
        self.client.put(key, value)
        retrieved = self.client.get(key)
        self.assertEqual(len(retrieved), len(value))
        self.assertEqual(retrieved, value)

if __name__ == "__main__":
    unittest.main()