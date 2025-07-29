import unittest
import random
import string
from resilient_kvs.distributed_kv_store import DistributedKVStore

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        self.node_id = "node_1"
        self.nodes = ["node_1", "node_2", "node_3", "node_4", "node_5"]
        def get_node_list():
            return self.nodes.copy()
        self.kv_store = DistributedKVStore(self.node_id, get_node_list)

    def test_basic_put_get(self):
        key = random_string()
        value = random_string()
        self.kv_store.put(key, value)
        self.assertEqual(self.kv_store.get(key), value)

    def test_get_nonexistent_key(self):
        self.assertIsNone(self.kv_store.get(random_string()))

    def test_delete_key(self):
        key = random_string()
        value = random_string()
        self.kv_store.put(key, value)
        self.kv_store.delete(key)
        self.assertIsNone(self.kv_store.get(key))

    def test_replication(self):
        key = random_string()
        value = random_string()
        self.kv_store.put(key, value)
        
        # Simulate node failures by removing nodes one by one
        for node_to_remove in self.nodes[:3]:
            self.nodes.remove(node_to_remove)
            self.assertEqual(self.kv_store.get(key), value)

    def test_concurrent_operations(self):
        keys = [random_string() for _ in range(100)]
        values = [random_string() for _ in range(100)]
        
        # Test concurrent puts
        for k, v in zip(keys, values):
            self.kv_store.put(k, v)
        
        # Verify all puts
        for k, v in zip(keys, values):
            self.assertEqual(self.kv_store.get(k), v)
        
        # Test concurrent deletes
        for k in keys[:50]:
            self.kv_store.delete(k)
        
        # Verify deletes and remaining puts
        for i, k in enumerate(keys):
            if i < 50:
                self.assertIsNone(self.kv_store.get(k))
            else:
                self.assertEqual(self.kv_store.get(k), values[i])

    def test_large_key_value(self):
        large_key = random_string(1024*1024)  # 1MB key
        large_value = random_string(1024*1024)  # 1MB value
        self.kv_store.put(large_key, large_value)
        self.assertEqual(self.kv_store.get(large_key), large_value)

    def test_node_addition(self):
        key = random_string()
        value = random_string()
        self.kv_store.put(key, value)
        
        # Add new nodes
        self.nodes.extend(["node_6", "node_7", "node_8"])
        self.assertEqual(self.kv_store.get(key), value)

    def test_data_redistribution_after_node_failure(self):
        # Store multiple keys
        test_data = {random_string(): random_string() for _ in range(100)}
        for k, v in test_data.items():
            self.kv_store.put(k, v)
        
        # Remove a node and verify all keys are still accessible
        failed_node = random.choice(self.nodes)
        self.nodes.remove(failed_node)
        
        for k, v in test_data.items():
            self.assertEqual(self.kv_store.get(k), v)

    def test_eventual_consistency(self):
        key = random_string()
        initial_value = random_string()
        updated_value = random_string()
        
        self.kv_store.put(key, initial_value)
        self.assertEqual(self.kv_store.get(key), initial_value)
        
        self.kv_store.put(key, updated_value)
        self.assertEqual(self.kv_store.get(key), updated_value)

if __name__ == '__main__':
    unittest.main()