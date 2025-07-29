import unittest
import threading
import time
from consistent_hashing import DistributedHashStore

class DistributedHashStoreTest(unittest.TestCase):
    def setUp(self):
        # Initialize a distributed key-value store with three initial nodes.
        self.store = DistributedHashStore()
        self.store.add_node("node1")
        self.store.add_node("node2")
        self.store.add_node("node3")
    
    def test_put_and_get(self):
        # Test basic put and get operations.
        self.store.put("key1", "value1")
        self.store.put("key2", "value2")
        self.store.put("key3", "value3")
        
        self.assertEqual(self.store.get("key1"), "value1")
        self.assertEqual(self.store.get("key2"), "value2")
        self.assertEqual(self.store.get("key3"), "value3")
        self.assertIsNone(self.store.get("nonexistent"))
    
    def test_add_node_redistribution(self):
        # Add multiple keys, then add a new node and confirm that keys are still available.
        keys = {"alpha": "A", "beta": "B", "gamma": "C", "delta": "D"}
        for k, v in keys.items():
            self.store.put(k, v)
        
        # Add a new node which should trigger redistribution.
        self.store.add_node("node4")
        
        # Allow some time for any asynchronous redistribution if applicable.
        time.sleep(0.1)
        
        for k, v in keys.items():
            self.assertEqual(self.store.get(k), v)
    
    def test_remove_node_redistribution(self):
        # Add keys and then remove a node to ensure keys are redistributed.
        keys = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in keys.items():
            self.store.put(k, v)
        
        # Remove one node.
        self.store.remove_node("node2")
        
        # Allow some time for redistribution.
        time.sleep(0.1)
        
        for k, v in keys.items():
            self.assertEqual(self.store.get(k), v)
    
    def test_concurrent_operations(self):
        # Test thread-safety by performing concurrent add, remove, put, and get operations.
        def add_and_put():
            for i in range(10, 20):
                node_id = f"node{i}"
                self.store.add_node(node_id)
                self.store.put(f"key_{i}", f"value_{i}")
                time.sleep(0.005)
        
        def remove_nodes():
            # Remove node1 and node3 concurrently with other operations.
            nodes_to_remove = ["node1", "node3"]
            for node in nodes_to_remove:
                time.sleep(0.01)
                self.store.remove_node(node)
        
        def get_keys():
            # Attempt to get keys repeatedly.
            for _ in range(50):
                # Access keys that may or may not exist.
                for i in range(10, 20):
                    _ = self.store.get(f"key_{i}")
                time.sleep(0.002)
        
        threads = []
        t1 = threading.Thread(target=add_and_put)
        t2 = threading.Thread(target=remove_nodes)
        t3 = threading.Thread(target=get_keys)
        
        threads.extend([t1, t2, t3])
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # After all threads complete, verify that keys added are available.
        for i in range(10, 20):
            expected_value = f"value_{i}"
            self.assertEqual(self.store.get(f"key_{i}"), expected_value)
    
    def test_multiple_operations_sequence(self):
        # Sequentially perform operations to simulate real-world usage.
        operations = [
            ("put", "user1", "Alice"),
            ("put", "user2", "Bob"),
            ("put", "user3", "Charlie"),
            ("get", "user1", "Alice"),
            ("get", "user2", "Bob"),
            ("add_node", "node4"),
            ("put", "user4", "Diana"),
            ("get", "user3", "Charlie"),
            ("remove_node", "node2"),
            ("get", "user4", "Diana")
        ]
        
        for op in operations:
            if op[0] == "put":
                self.store.put(op[1], op[2])
            elif op[0] == "get":
                result = self.store.get(op[1])
                self.assertEqual(result, op[2])
            elif op[0] == "add_node":
                self.store.add_node(op[1])
            elif op[0] == "remove_node":
                self.store.remove_node(op[1])
        
        # Final verification of all keys.
        expected_data = {
            "user1": "Alice",
            "user2": "Bob",
            "user3": "Charlie",
            "user4": "Diana"
        }
        for k, v in expected_data.items():
            self.assertEqual(self.store.get(k), v)

if __name__ == "__main__":
    unittest.main()