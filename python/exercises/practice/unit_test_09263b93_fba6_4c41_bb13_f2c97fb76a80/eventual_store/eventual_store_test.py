import unittest
from eventual_store import Node


class TestEventualStore(unittest.TestCase):
    def test_basic_put_get(self):
        node = Node()
        node.put("key1", "value1", 100)
        self.assertEqual(node.get("key1"), "value1")
        
        # Overwrite with newer timestamp
        node.put("key1", "value2", 200)
        self.assertEqual(node.get("key1"), "value2")
        
        # Try to overwrite with older timestamp (should be ignored)
        node.put("key1", "value3", 50)
        self.assertEqual(node.get("key1"), "value2")
        
        # Same timestamp - new value should overwrite
        node.put("key1", "value4", 200)
        self.assertEqual(node.get("key1"), "value4")

    def test_get_nonexistent_key(self):
        node = Node()
        self.assertIsNone(node.get("nonexistent"))

    def test_simple_reconciliation(self):
        node1 = Node()
        node2 = Node()
        
        # Add different data to each node
        node1.put("key1", "node1_value1", 100)
        node2.put("key2", "node2_value1", 100)
        
        # Reconcile
        node1.reconcile(node2)
        
        # Each node should have all keys
        self.assertEqual(node1.get("key1"), "node1_value1")
        self.assertEqual(node1.get("key2"), "node2_value1")
        self.assertEqual(node2.get("key1"), "node1_value1")
        self.assertEqual(node2.get("key2"), "node2_value1")
        
    def test_reconciliation_with_conflicts(self):
        node1 = Node()
        node2 = Node()
        
        # Add conflicting data
        node1.put("key1", "node1_value1", 100)
        node2.put("key1", "node2_value1", 200)  # Newer timestamp
        
        # Reconcile
        node1.reconcile(node2)
        
        # Both nodes should have the newer value
        self.assertEqual(node1.get("key1"), "node2_value1")
        self.assertEqual(node2.get("key1"), "node2_value1")
        
    def test_reconciliation_with_same_timestamp(self):
        node1 = Node()
        node2 = Node()
        
        # Add data with same timestamp but different values
        node1.put("key1", "node1_value1", 100)
        node2.put("key1", "node2_value1", 100)
        
        # Before reconcile, each node has its own value
        self.assertEqual(node1.get("key1"), "node1_value1")
        self.assertEqual(node2.get("key1"), "node2_value1")
        
        # Reconcile
        node1.reconcile(node2)
        
        # After reconcile, values should be consistent
        # Implementation can choose which value to keep, but both nodes must be consistent
        val1 = node1.get("key1")
        val2 = node2.get("key1")
        self.assertEqual(val1, val2)
        self.assertTrue(val1 in ["node1_value1", "node2_value1"])
        
    def test_multi_node_reconciliation(self):
        nodes = [Node() for _ in range(5)]
        
        # Add different data to each node
        for i, node in enumerate(nodes):
            node.put(f"key{i}", f"value{i}", 100 + i)
            
        # Reconcile all nodes
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                nodes[i].reconcile(nodes[j])
        
        # All nodes should have all keys with the correct values
        for node in nodes:
            for i in range(len(nodes)):
                self.assertEqual(node.get(f"key{i}"), f"value{i}")
                
    def test_efficient_reconciliation(self):
        node1 = Node()
        node2 = Node()
        
        # Setup some initial state on both nodes
        common_keys = ["common1", "common2", "common3"]
        for key in common_keys:
            node1.put(key, f"value_{key}", 100)
            node2.put(key, f"value_{key}", 100)
        
        # Add unique keys to each node
        node1.put("unique1", "node1_unique", 200)
        node2.put("unique2", "node2_unique", 200)
        
        # Add a key with a newer timestamp on node1
        node1.put("update1", "node1_newer", 300)
        node2.put("update1", "node2_older", 200)
        
        # Add a key with a newer timestamp on node2
        node1.put("update2", "node1_older", 200)
        node2.put("update2", "node2_newer", 300)
        
        # Test reconciliation transfers only what's needed
        # This is a bit harder to test directly, so we verify correct final state
        node1.reconcile(node2)
        
        # Verify common keys are unchanged
        for key in common_keys:
            self.assertEqual(node1.get(key), f"value_{key}")
            self.assertEqual(node2.get(key), f"value_{key}")
        
        # Verify unique keys are shared
        self.assertEqual(node1.get("unique1"), "node1_unique")
        self.assertEqual(node1.get("unique2"), "node2_unique")
        self.assertEqual(node2.get("unique1"), "node1_unique")
        self.assertEqual(node2.get("unique2"), "node2_unique")
        
        # Verify newer values win
        self.assertEqual(node1.get("update1"), "node1_newer")
        self.assertEqual(node2.get("update1"), "node1_newer")
        self.assertEqual(node1.get("update2"), "node2_newer")
        self.assertEqual(node2.get("update2"), "node2_newer")
        
    def test_network_partition_scenario(self):
        """Simulates a network partition scenario"""
        # Create 3 nodes
        node_a = Node()
        node_b = Node()
        node_c = Node()
        
        # Initial state - all nodes are in sync
        node_a.put("key1", "value1", 100)
        node_b.reconcile(node_a)
        node_c.reconcile(node_a)
        
        # Simulate network partition: 
        # node_a can communicate with node_b
        # node_c is isolated
        
        # Updates during partition
        node_a.put("key1", "new_value1", 200)
        node_a.put("key2", "value2", 200)
        node_c.put("key3", "value3", 300)
        
        # Synchronize node_a and node_b during partition
        node_a.reconcile(node_b)
        
        # Verify node_a and node_b are in sync
        self.assertEqual(node_a.get("key1"), "new_value1")
        self.assertEqual(node_a.get("key2"), "value2")
        self.assertIsNone(node_a.get("key3"))
        
        self.assertEqual(node_b.get("key1"), "new_value1")
        self.assertEqual(node_b.get("key2"), "value2")
        self.assertIsNone(node_b.get("key3"))
        
        # Verify node_c has its own state
        self.assertEqual(node_c.get("key1"), "value1")  # old value
        self.assertIsNone(node_c.get("key2"))
        self.assertEqual(node_c.get("key3"), "value3")
        
        # Partition heals - reconcile all nodes
        node_a.reconcile(node_c)
        node_b.reconcile(node_c)
        
        # Verify all nodes are now in sync
        self.assertEqual(node_a.get("key1"), "new_value1")
        self.assertEqual(node_a.get("key2"), "value2")
        self.assertEqual(node_a.get("key3"), "value3")
        
        self.assertEqual(node_b.get("key1"), "new_value1")
        self.assertEqual(node_b.get("key2"), "value2")
        self.assertEqual(node_b.get("key3"), "value3")
        
        self.assertEqual(node_c.get("key1"), "new_value1")
        self.assertEqual(node_c.get("key2"), "value2")
        self.assertEqual(node_c.get("key3"), "value3")


if __name__ == "__main__":
    unittest.main()