import unittest
from edge_router import optimize_router_placement

class EdgeRouterTest(unittest.TestCase):
    def test_simple_line_graph(self):
        # Simple line graph where placing router in the middle makes most sense
        n = 3
        edges = [(0, 1), (1, 2)]
        k = 1
        server_weights = [1, 1, 1]
        
        # Expected result should place the router at node 1 (middle)
        result = optimize_router_placement(n, edges, k, server_weights)
        
        # Check result format
        self.assertEqual(len(result), k)
        self.assertIn(1, result)  # Router should be at node 1
        
        # Manually calculate weighted average latency
        # With router at node 1:
        # - Node 0: 1 hop to router, weighted 1*1 = 1
        # - Node 1: 0 hops to router, weighted 1*0 = 0
        # - Node 2: 1 hop to router, weighted 1*1 = 1
        # Total weighted latency: 2
        # Total weight: 3
        # Expected average: 2/3 ≈ 0.67
        
    def test_star_graph(self):
        # Star graph with center at node 0, placing router at center is optimal
        n = 5
        edges = [(0, 1), (0, 2), (0, 3), (0, 4)]
        k = 1
        server_weights = [1, 1, 1, 1, 1]
        
        result = optimize_router_placement(n, edges, k, server_weights)
        
        self.assertEqual(len(result), k)
        self.assertIn(0, result)  # Router should be at node 0 (center)

    def test_complex_graph(self):
        # More complex graph
        n = 6
        edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5)]
        k = 2
        server_weights = [1, 2, 1, 3, 1, 1]
        
        result = optimize_router_placement(n, edges, k, server_weights)
        
        # Check format
        self.assertEqual(len(result), k)
        for node in result:
            self.assertTrue(0 <= node < n)
        
        # Given the weights, nodes 1 and 3 should be prioritized
        # but different algorithms might give different but valid results
        
    def test_complete_graph(self):
        # In a complete graph, any k nodes are optimal (all nodes connected)
        n = 4
        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        k = 2
        server_weights = [1, 1, 1, 1]
        
        result = optimize_router_placement(n, edges, k, server_weights)
        
        self.assertEqual(len(result), k)
        self.assertEqual(len(set(result)), k)  # Ensure unique nodes
        
    def test_multiple_components_simple(self):
        # Two disconnected components
        n = 6
        edges = [(0, 1), (1, 2), (3, 4), (4, 5)]
        k = 2
        server_weights = [1, 1, 1, 1, 1, 1]
        
        # This should raise a ValueError since the graph is not connected
        with self.assertRaises(ValueError):
            optimize_router_placement(n, edges, k, server_weights)
    
    def test_weighted_servers(self):
        # Test with varied server weights
        n = 5
        edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        k = 1
        server_weights = [1, 10, 1, 1, 1]  # Node 1 has high weight
        
        result = optimize_router_placement(n, edges, k, server_weights)
        
        self.assertEqual(len(result), k)
        # Node 1 or adjacent nodes should be prioritized due to weight
        self.assertTrue(0 in result or 1 in result or 2 in result)
    
    def test_k_equals_n(self):
        # When k equals n, all nodes should have routers
        n = 4
        edges = [(0, 1), (1, 2), (2, 3)]
        k = 4
        server_weights = [1, 1, 1, 1]
        
        result = optimize_router_placement(n, edges, k, server_weights)
        
        self.assertEqual(len(result), k)
        # All nodes should have routers
        self.assertEqual(set(result), set(range(n)))
    
    def test_k_equals_one(self):
        # When k=1, the optimal placement depends on the graph structure and weights
        n = 7
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (3, 6)]
        k = 1
        server_weights = [1, 1, 1, 10, 1, 1, 1]  # Node 3 has high weight
        
        result = optimize_router_placement(n, edges, k, server_weights)
        
        self.assertEqual(len(result), k)
        # Given high weight at node 3, it should be selected
        self.assertEqual(result[0], 3)

    def test_large_graph(self):
        # Test with a larger graph (this is a performance test)
        n = 100
        # Create a line graph
        edges = [(i, i+1) for i in range(n-1)]
        k = 5
        server_weights = [1] * n
        
        result = optimize_router_placement(n, edges, k, server_weights)
        
        self.assertEqual(len(result), k)
        self.assertEqual(len(set(result)), k)  # Check for unique nodes
        
    def test_invalid_inputs(self):
        # Test with invalid inputs
        
        # k > n (invalid)
        with self.assertRaises(ValueError):
            optimize_router_placement(3, [(0, 1), (1, 2)], 4, [1, 1, 1])
        
        # Negative k (invalid)
        with self.assertRaises(ValueError):
            optimize_router_placement(3, [(0, 1), (1, 2)], -1, [1, 1, 1])
        
        # Invalid edge (node index out of range)
        with self.assertRaises(ValueError):
            optimize_router_placement(3, [(0, 1), (1, 3)], 1, [1, 1, 1])
        
        # Wrong number of weights
        with self.assertRaises(ValueError):
            optimize_router_placement(3, [(0, 1), (1, 2)], 1, [1, 1])
        
        # Zero weights (invalid)
        with self.assertRaises(ValueError):
            optimize_router_placement(3, [(0, 1), (1, 2)], 1, [1, 0, 1])

if __name__ == '__main__':
    unittest.main()