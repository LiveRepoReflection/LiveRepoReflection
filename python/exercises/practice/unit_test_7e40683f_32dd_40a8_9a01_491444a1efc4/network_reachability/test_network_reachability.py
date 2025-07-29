import unittest
from network_reachability import is_reachable


class NetworkReachabilityTest(unittest.TestCase):
    def test_direct_connection(self):
        node_data = [
            (1, [2], []),
            (2, [], [])
        ]
        self.assertTrue(is_reachable(node_data, 1, 2, 1))
        self.assertFalse(is_reachable(node_data, 2, 1, 1))
    
    def test_two_hop_connection(self):
        node_data = [
            (1, [2], []),
            (2, [3], []),
            (3, [], [])
        ]
        self.assertTrue(is_reachable(node_data, 1, 3, 2))
        self.assertFalse(is_reachable(node_data, 1, 3, 1))
    
    def test_multiple_paths(self):
        node_data = [
            (1, [2, 3], []),
            (2, [4], []),
            (3, [4], []),
            (4, [], [])
        ]
        self.assertTrue(is_reachable(node_data, 1, 4, 2))
        self.assertFalse(is_reachable(node_data, 4, 1, 3))
    
    def test_distant_nodes(self):
        node_data = [
            (1, [2], [5]),
            (2, [], []),
            (5, [6], []),
            (6, [], [])
        ]
        # Should not use distant nodes for direct path finding
        self.assertFalse(is_reachable(node_data, 1, 5, 1))
        self.assertFalse(is_reachable(node_data, 1, 6, 2))
    
    def test_complex_network(self):
        node_data = [
            (1, [2, 3], [5]),
            (2, [4], [6]),
            (3, [4], [7]),
            (4, [], [8]),
            (5, [6], [9]),
            (6, [], [10]),
            (7, [], [11]),
            (8, [], [12])
        ]
        self.assertTrue(is_reachable(node_data, 1, 4, 2))
        self.assertFalse(is_reachable(node_data, 1, 10, 2))  # Would need distant node knowledge
        self.assertFalse(is_reachable(node_data, 4, 1, 10))  # No path back
    
    def test_cyclic_paths(self):
        node_data = [
            (1, [2], []),
            (2, [3], []),
            (3, [4], []),
            (4, [1], [])
        ]
        self.assertTrue(is_reachable(node_data, 1, 4, 3))
        self.assertTrue(is_reachable(node_data, 1, 1, 4))  # Can come back to itself
    
    def test_unreachable_nodes(self):
        node_data = [
            (1, [2], []),
            (2, [3], []),
            (4, [5], []),
            (5, [6], [])
        ]
        self.assertFalse(is_reachable(node_data, 1, 4, 10))
        self.assertFalse(is_reachable(node_data, 1, 6, 5))
    
    def test_exact_hop_limit(self):
        node_data = [
            (1, [2], []),
            (2, [3], []),
            (3, [4], []),
            (4, [5], []),
            (5, [], [])
        ]
        self.assertTrue(is_reachable(node_data, 1, 4, 3))
        self.assertFalse(is_reachable(node_data, 1, 5, 3))
        self.assertTrue(is_reachable(node_data, 1, 5, 4))
    
    def test_large_network_simulation(self):
        # Build a larger network to test scalability
        node_data = []
        for i in range(1, 101):
            neighbors = [i + 1] if i < 100 else []
            distant = [i + 10] if i < 91 else []
            node_data.append((i, neighbors, distant))
        
        self.assertTrue(is_reachable(node_data, 1, 10, 9))
        self.assertTrue(is_reachable(node_data, 1, 20, 19))
        self.assertFalse(is_reachable(node_data, 1, 50, 10))
    
    def test_empty_network(self):
        self.assertFalse(is_reachable([], 1, 2, 3))
    
    def test_node_not_in_network(self):
        node_data = [
            (1, [2], []),
            (2, [], [])
        ]
        self.assertFalse(is_reachable(node_data, 1, 3, 2))
        self.assertFalse(is_reachable(node_data, 3, 1, 2))
    
    def test_zero_hops(self):
        node_data = [
            (1, [2], []),
            (2, [], [])
        ]
        self.assertTrue(is_reachable(node_data, 1, 1, 0))  # Node can reach itself with 0 hops
        self.assertFalse(is_reachable(node_data, 1, 2, 0))


if __name__ == '__main__':
    unittest.main()