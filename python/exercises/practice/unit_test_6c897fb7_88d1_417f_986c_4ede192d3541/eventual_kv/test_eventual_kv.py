import unittest
from time import sleep
from threading import Thread
from eventual_kv import Node

class TestEventualKV(unittest.TestCase):
    def setUp(self):
        self.node1 = Node()
        self.node2 = Node()
        self.node3 = Node()

    def test_basic_put_get(self):
        self.node1.put("key1", "value1")
        self.assertEqual(self.node1.get("key1"), "value1")
        self.assertIsNone(self.node1.get("nonexistent"))

    def test_basic_replication(self):
        self.node1.put("key1", "value1")
        self.node2.replicate(self.node1.get_all_data())
        self.assertEqual(self.node2.get("key1"), "value1")

    def test_last_write_wins(self):
        self.node1.put("key1", "value1")
        sleep(0.001)  # Ensure different timestamps
        self.node2.put("key1", "value2")
        
        # Replicate both ways
        self.node1.replicate(self.node2.get_all_data())
        self.node2.replicate(self.node1.get_all_data())
        
        # Both nodes should have the latest value
        self.assertEqual(self.node1.get("key1"), "value2")
        self.assertEqual(self.node2.get("key1"), "value2")

    def test_concurrent_updates(self):
        def update_node1():
            for i in range(100):
                self.node1.put(f"key{i}", f"value1_{i}")
                sleep(0.001)

        def update_node2():
            for i in range(100):
                self.node2.put(f"key{i}", f"value2_{i}")
                sleep(0.001)

        t1 = Thread(target=update_node1)
        t2 = Thread(target=update_node2)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Replicate both ways
        self.node1.replicate(self.node2.get_all_data())
        self.node2.replicate(self.node1.get_all_data())

        # Verify consistency
        for i in range(100):
            self.assertEqual(self.node1.get(f"key{i}"), self.node2.get(f"key{i}"))

    def test_multi_node_replication(self):
        # Initial data in node1
        self.node1.put("key1", "value1")
        self.node1.put("key2", "value2")
        
        sleep(0.001)  # Ensure different timestamps
        
        # Different updates in node2
        self.node2.put("key2", "value2_updated")
        self.node2.put("key3", "value3")
        
        sleep(0.001)  # Ensure different timestamps
        
        # Different updates in node3
        self.node3.put("key3", "value3_updated")
        self.node3.put("key4", "value4")

        # Replicate across all nodes
        self.node1.replicate(self.node2.get_all_data())
        self.node1.replicate(self.node3.get_all_data())
        self.node2.replicate(self.node1.get_all_data())
        self.node2.replicate(self.node3.get_all_data())
        self.node3.replicate(self.node1.get_all_data())
        self.node3.replicate(self.node2.get_all_data())

        # Verify consistency across all nodes
        expected_values = {
            "key1": "value1",
            "key2": "value2_updated",
            "key3": "value3_updated",
            "key4": "value4"
        }

        for key, value in expected_values.items():
            self.assertEqual(self.node1.get(key), value)
            self.assertEqual(self.node2.get(key), value)
            self.assertEqual(self.node3.get(key), value)

    def test_optimized_replication(self):
        # Set initial data with older timestamp
        self.node1.put("key1", "old_value")
        sleep(0.001)  # Ensure different timestamps
        
        # Update with newer timestamp
        self.node2.put("key1", "new_value")
        
        # Get initial data size
        initial_data = self.node2.get_all_data()
        
        # Replicate older data to node2
        self.node2.replicate(self.node1.get_all_data())
        
        # Verify that newer value remains
        self.assertEqual(self.node2.get("key1"), "new_value")
        
        # Verify that node2's data is unchanged
        self.assertEqual(self.node2.get_all_data(), initial_data)

    def test_empty_operations(self):
        # Test empty get
        self.assertIsNone(self.node1.get("nonexistent"))
        
        # Test empty replicate
        self.node1.replicate({})
        self.assertEqual(self.node1.get_all_data(), {})

if __name__ == '__main__':
    unittest.main()