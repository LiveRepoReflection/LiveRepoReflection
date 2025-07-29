import unittest
from delivery_network import optimal_routes


class DeliveryNetworkTest(unittest.TestCase):
    def test_simple_case(self):
        n = 5
        edges = [
            (0, 1, 10, 0.9),
            (0, 2, 15, 0.8),
            (1, 3, 12, 0.7),
            (2, 3, 8, 0.95),
            (3, 4, 5, 0.99)
        ]
        source = 0
        destinations = [3, 4]
        alpha = 1.0
        beta = 1.0

        result = optimal_routes(n, edges, source, destinations, alpha, beta)
        
        # The correct path for node 3 should be either [0, 1, 3] or [0, 2, 3]
        # Calculating scores:
        # Path [0, 1, 3]: Score = (0.9 * 0.7)^1 / (10 + 12)^1 = 0.63 / 22 ≈ 0.0286
        # Path [0, 2, 3]: Score = (0.8 * 0.95)^1 / (15 + 8)^1 = 0.76 / 23 ≈ 0.0330
        # [0, 2, 3] should be chosen as it has the higher score
        
        # For node 4, the path can be [0, 1, 3, 4] or [0, 2, 3, 4]
        # Path [0, 1, 3, 4]: Score = (0.9 * 0.7 * 0.99)^1 / (10 + 12 + 5)^1 = 0.6237 / 27 ≈ 0.0231
        # Path [0, 2, 3, 4]: Score = (0.8 * 0.95 * 0.99)^1 / (15 + 8 + 5)^1 = 0.7524 / 28 ≈ 0.0269
        # [0, 2, 3, 4] should be chosen as it has the higher score

        self.assertIn(result[3], [[0, 1, 3], [0, 2, 3]])
        self.assertIn(result[4], [[0, 1, 3, 4], [0, 2, 3, 4]])
        
        # Double-check by checking if received path is valid
        for dest, path in result.items():
            self.assertEqual(path[0], source)
            self.assertEqual(path[-1], dest)
            # Check that path is contiguous in the graph
            for i in range(len(path) - 1):
                edge_exists = False
                for e in edges:
                    if e[0] == path[i] and e[1] == path[i+1]:
                        edge_exists = True
                        break
                self.assertTrue(edge_exists, f"Edge from {path[i]} to {path[i+1]} does not exist in the graph")

    def test_single_destination(self):
        n = 3
        edges = [
            (0, 1, 5, 0.8),
            (0, 2, 10, 0.9)
        ]
        source = 0
        destinations = [2]
        alpha = 1.0
        beta = 1.0

        result = optimal_routes(n, edges, source, destinations, alpha, beta)
        
        self.assertEqual(result[2], [0, 2])

    def test_no_valid_path(self):
        n = 4
        edges = [
            (0, 1, 5, 0.8),
            (0, 2, 10, 0.9)
        ]
        source = 0
        destinations = [3]
        alpha = 1.0
        beta = 1.0

        result = optimal_routes(n, edges, source, destinations, alpha, beta)
        
        self.assertEqual(result[3], [])

    def test_different_alpha_beta_weights(self):
        n = 3
        edges = [
            (0, 1, 10, 0.9),  # Low cost, high reliability
            (0, 2, 5, 0.5)    # High cost, low reliability
        ]
        source = 0
        destinations = [1, 2]
        
        # High alpha (prioritize reliability)
        result_high_alpha = optimal_routes(n, edges, source, destinations, 3.0, 1.0)
        self.assertEqual(result_high_alpha[1], [0, 1])  # Should choose the high reliability path
        
        # High beta (prioritize cost)
        result_high_beta = optimal_routes(n, edges, source, destinations, 1.0, 3.0)
        self.assertEqual(result_high_beta[2], [0, 2])  # Should choose the low cost path

    def test_larger_graph(self):
        n = 8
        edges = [
            (0, 1, 10, 0.9),
            (0, 2, 15, 0.8),
            (1, 3, 12, 0.7),
            (2, 3, 8, 0.95),
            (3, 4, 5, 0.99),
            (1, 5, 7, 0.85),
            (5, 6, 9, 0.92),
            (4, 6, 6, 0.93),
            (6, 7, 8, 0.97)
        ]
        source = 0
        destinations = [4, 6, 7]
        alpha = 1.0
        beta = 1.0

        result = optimal_routes(n, edges, source, destinations, alpha, beta)
        
        # Verify that paths exist for all destinations
        self.assertIn(4, result)
        self.assertIn(6, result)
        self.assertIn(7, result)
        
        # Check that all paths start at source and end at the correct destination
        for dest, path in result.items():
            if path:  # Only check if a path exists
                self.assertEqual(path[0], source)
                self.assertEqual(path[-1], dest)

    def test_bidirectional_graph(self):
        n = 5
        edges = [
            (0, 1, 10, 0.9),
            (1, 0, 10, 0.9),  # Bidirectional edge
            (0, 2, 15, 0.8),
            (2, 0, 15, 0.8),  # Bidirectional edge
            (1, 3, 12, 0.7),
            (3, 1, 12, 0.7),  # Bidirectional edge
            (2, 3, 8, 0.95),
            (3, 2, 8, 0.95),  # Bidirectional edge
            (3, 4, 5, 0.99),
            (4, 3, 5, 0.99)   # Bidirectional edge
        ]
        source = 0
        destinations = [4]
        alpha = 1.0
        beta = 1.0

        result = optimal_routes(n, edges, source, destinations, alpha, beta)
        
        self.assertTrue(len(result[4]) > 0)
        self.assertEqual(result[4][0], source)
        self.assertEqual(result[4][-1], 4)

    def test_duplicate_edges(self):
        n = 4
        edges = [
            (0, 1, 10, 0.9),
            (0, 1, 5, 0.8),  # Duplicate edge with different cost/reliability
            (1, 2, 7, 0.85),
            (2, 3, 6, 0.95)
        ]
        source = 0
        destinations = [3]
        alpha = 1.0
        beta = 1.0

        result = optimal_routes(n, edges, source, destinations, alpha, beta)
        
        self.assertEqual(result[3][0], source)
        self.assertEqual(result[3][-1], 3)

    def test_zero_alpha_beta(self):
        n = 3
        edges = [
            (0, 1, 10, 0.9),
            (0, 2, 5, 0.5)
        ]
        source = 0
        destinations = [1, 2]
        
        # If alpha and beta are both zero, any path should be acceptable
        result = optimal_routes(n, edges, source, destinations, 0.0, 0.0)
        
        # Just verify that valid paths are returned
        for dest, path in result.items():
            if path:  # Only check if a path exists
                self.assertEqual(path[0], source)
                self.assertEqual(path[-1], dest)

    def test_negative_path_detection(self):
        n = 6
        edges = [
            (0, 1, 10, 0.9),
            (1, 2, 12, 0.8),
            (2, 3, 8, 0.7),
            (3, 1, 5, 0.6),  # Creates a cycle: 1->2->3->1
            (0, 4, 15, 0.95),
            (4, 5, 7, 0.9)
        ]
        source = 0
        destinations = [5]
        alpha = 1.0
        beta = 1.0

        result = optimal_routes(n, edges, source, destinations, alpha, beta)
        
        # Verify the path doesn't have cycles
        if result[5]:
            seen = set()
            for node in result[5]:
                self.assertNotIn(node, seen, "Cycle detected in the path")
                seen.add(node)

if __name__ == '__main__':
    unittest.main()