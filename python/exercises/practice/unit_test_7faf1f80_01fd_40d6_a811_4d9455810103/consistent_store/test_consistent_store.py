import unittest
import hashlib
from consistent_store import ConsistentStore

class TestConsistentStore(unittest.TestCase):
    def setUp(self):
        self.store = ConsistentStore(virtual_nodes=100)
    
    def test_add_node(self):
        self.store.add_node("server1")
        self.assertIn("server1", [n.split('-')[0] for n in self.store.nodes])
        
        with self.assertRaises(ValueError):
            self.store.add_node("server1")  # duplicate node
    
    def test_remove_node(self):
        self.store.add_node("server1")
        self.store.remove_node("server1")
        self.assertNotIn("server1", [n.split('-')[0] for n in self.store.nodes])
        
        with self.assertRaises(ValueError):
            self.store.remove_node("nonexistent")
    
    def test_put_get(self):
        self.store.add_node("server1")
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        self.assertIsNone(self.store.get("nonexistent"))
    
    def test_node_assignment(self):
        self.store.add_node("server1")
        self.store.add_node("server2")
        
        key = "test_key"
        md5_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)
        node_id = self.store.get_node(key)
        self.assertTrue(node_id.startswith("server"))
    
    def test_data_migration_add(self):
        self.store.add_node("server1")
        self.store.put("key1", "value1")
        self.store.add_node("server2")
        
        # Verify key1 might have moved to server2
        node = self.store.get_node("key1")
        self.assertTrue(node.startswith(("server1", "server2")))
    
    def test_data_migration_remove(self):
        self.store.add_node("server1")
        self.store.add_node("server2")
        self.store.put("key1", "value1")
        original_node = self.store.get_node("key1")
        
        self.store.remove_node(original_node.split('-')[0])
        new_node = self.store.get_node("key1")
        self.assertNotEqual(original_node, new_node)
    
    def test_concurrent_access(self):
        import threading
        
        self.store.add_node("server1")
        results = []
        
        def worker(key, value):
            self.store.put(key, value)
            results.append(self.store.get(key))
        
        threads = [
            threading.Thread(target=worker, args=(f"key{i}", f"value{i}"))
            for i in range(100)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        self.assertEqual(len(results), 100)
        self.assertEqual(len(set(results)), 100)
    
    def test_virtual_nodes_distribution(self):
        self.store = ConsistentStore(virtual_nodes=1000)
        self.store.add_node("server1")
        self.store.add_node("server2")
        
        assignments = {}
        for i in range(10000):
            key = f"key{i}"
            node = self.store.get_node(key).split('-')[0]
            assignments[node] = assignments.get(node, 0) + 1
        
        # Verify roughly even distribution
        ratio = assignments["server1"] / assignments["server2"]
        self.assertTrue(0.9 < ratio < 1.1)

if __name__ == '__main__':
    unittest.main()