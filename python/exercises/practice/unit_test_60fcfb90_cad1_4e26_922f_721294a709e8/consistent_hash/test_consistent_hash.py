import unittest
import random
import string
from consistent_hash import ConsistentHash

class TestConsistentHash(unittest.TestCase):
    def setUp(self):
        self.ch = ConsistentHash()
        self.node_ids = [0, 1, 2, 3, 4]
        self.test_keys = [
            ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            for _ in range(100)
        ]

    def test_empty_cluster(self):
        self.assertEqual(self.ch.get_node("any_key"), -1)

    def test_single_node(self):
        self.ch.add_node(0)
        for key in self.test_keys:
            self.assertEqual(self.ch.get_node(key), 0)

    def test_add_nodes(self):
        for node_id in self.node_ids:
            self.ch.add_node(node_id)
        
        for key in self.test_keys:
            self.assertIn(self.ch.get_node(key), self.node_ids)

    def test_remove_node(self):
        for node_id in self.node_ids:
            self.ch.add_node(node_id)
        
        removed_node = 2
        self.ch.remove_node(removed_node)
        
        for key in self.test_keys:
            node = self.ch.get_node(key)
            self.assertIn(node, self.node_ids)
            self.assertNotEqual(node, removed_node)

    def test_virtual_nodes_distribution(self):
        self.ch = ConsistentHash(vnodes=100)
        self.ch.add_node(0)
        self.ch.add_node(1)
        
        distribution = {0: 0, 1: 0}
        for key in self.test_keys:
            node = self.ch.get_node(key)
            distribution[node] += 1
        
        # Check if distribution is roughly even (within 20% difference)
        ratio = distribution[0] / distribution[1]
        self.assertTrue(0.8 < ratio < 1.2)

    def test_minimal_redistribution(self):
        for node_id in self.node_ids[:3]:
            self.ch.add_node(node_id)
        
        initial_mapping = {key: self.ch.get_node(key) for key in self.test_keys}
        
        self.ch.add_node(3)
        changed = 0
        for key in self.test_keys:
            if self.ch.get_node(key) != initial_mapping[key]:
                changed += 1
        
        # Expect less than 40% keys to change (1 new node out of 4)
        self.assertLess(changed, len(self.test_keys) * 0.4)

    def test_node_failure_handling(self):
        for node_id in self.node_ids:
            self.ch.add_node(node_id)
        
        failed_node = 1
        initial_mapping = {key: self.ch.get_node(key) for key in self.test_keys}
        
        self.ch.remove_node(failed_node)
        for key in self.test_keys:
            if initial_mapping[key] == failed_node:
                self.assertNotEqual(self.ch.get_node(key), failed_node)
            else:
                self.assertEqual(self.ch.get_node(key), initial_mapping[key])

    def test_consistent_hashing_property(self):
        for node_id in self.node_ids[:3]:
            self.ch.add_node(node_id)
        
        initial_mapping = {key: self.ch.get_node(key) for key in self.test_keys}
        
        # Add new node and verify only necessary keys moved
        self.ch.add_node(3)
        for key in self.test_keys:
            original_node = initial_mapping[key]
            new_node = self.ch.get_node(key)
            if new_node != original_node:
                self.assertEqual(new_node, 3)

    def test_duplicate_node_id(self):
        self.ch.add_node(0)
        with self.assertRaises(ValueError):
            self.ch.add_node(0)

    def test_remove_nonexistent_node(self):
        with self.assertRaises(ValueError):
            self.ch.remove_node(99)

if __name__ == '__main__':
    unittest.main()