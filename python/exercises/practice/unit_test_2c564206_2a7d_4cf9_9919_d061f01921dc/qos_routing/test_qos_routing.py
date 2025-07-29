import unittest
from qos_routing import find_best_paths

class TestQoSRouting(unittest.TestCase):
    def test_simple_network(self):
        """Test with a simple network with a clear best path."""
        n = 3
        edges = [(0, 1, 10, 100, 5), (1, 2, 10, 100, 5)]
        source = 0
        destination = 2
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 1

        expected = [[0, 1, 2]]
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)

    def test_multiple_paths(self):
        """Test with a network that has multiple valid paths."""
        n = 4
        edges = [
            (0, 1, 10, 100, 5),
            (1, 3, 10, 100, 5),
            (0, 2, 15, 120, 3),
            (2, 3, 10, 90, 4)
        ]
        source = 0
        destination = 3
        min_bandwidth = 50
        max_latency = 30
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 2

        # Paths should be sorted by score
        expected = [[0, 1, 3], [0, 2, 3]]
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)

    def test_bandwidth_constraint(self):
        """Test with a path that doesn't meet the bandwidth constraint."""
        n = 3
        edges = [(0, 1, 10, 40, 5), (1, 2, 10, 100, 5)]
        source = 0
        destination = 2
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 1

        expected = []  # No valid path meets the bandwidth constraint
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)

    def test_latency_constraint(self):
        """Test with a path that doesn't meet the latency constraint."""
        n = 3
        edges = [(0, 1, 15, 100, 5), (1, 2, 15, 100, 5)]
        source = 0
        destination = 2
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 1

        expected = []  # No valid path meets the latency constraint
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)

    def test_disjointedness_penalty(self):
        """Test that disjointedness penalty affects path ranking."""
        n = 4
        edges = [
            (0, 1, 10, 100, 5),  # Path 1: 0 -> 1 -> 3
            (1, 3, 10, 100, 5),
            (0, 2, 11, 100, 5),  # Path 2: 0 -> 2 -> 3 (slightly worse latency)
            (2, 3, 11, 100, 5)
        ]
        source = 0
        destination = 3
        min_bandwidth = 50
        max_latency = 30
        w1, w2, w3, w4 = 1.0, 0.0, 0.0, 10.0  # Only care about latency and heavily penalize overlap
        k = 2

        # With high disjointedness penalty, the second-best path should be preferred
        # even if its latency is slightly worse
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        expected = [[0, 1, 3], [0, 2, 3]]
        self.assertEqual(result, expected)

    def test_same_source_destination(self):
        """Test with source and destination being the same node."""
        n = 3
        edges = [(0, 1, 10, 100, 5), (1, 2, 10, 100, 5)]
        source = 1
        destination = 1
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 1

        expected = [[1]]  # Path is just the node itself
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)

    def test_disconnected_graph(self):
        """Test with a disconnected graph."""
        n = 4
        edges = [(0, 1, 10, 100, 5), (2, 3, 10, 100, 5)]  # No path from 0 to 3
        source = 0
        destination = 3
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 1

        expected = []  # No valid path exists
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)

    def test_cyclic_graph(self):
        """Test with a graph containing cycles."""
        n = 3
        edges = [
            (0, 1, 5, 100, 5),
            (1, 2, 5, 100, 5),
            (2, 0, 5, 100, 5)  # Creates a cycle
        ]
        source = 0
        destination = 2
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 2

        # Should find direct path and possibly a longer path that uses the cycle
        expected = [[0, 1, 2]]
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result[0], expected[0])  # First path should be the direct one
        self.assertTrue(len(result) <= 2)  # Should find at most k paths

    def test_zero_weights(self):
        """Test with some weights set to zero."""
        n = 4
        edges = [
            (0, 1, 10, 100, 5),  # Path 1: Better latency and cost
            (1, 3, 10, 100, 5),
            (0, 2, 15, 200, 10),  # Path 2: Better bandwidth
            (2, 3, 15, 200, 10)
        ]
        source = 0
        destination = 3
        min_bandwidth = 50
        max_latency = 100
        
        # Only consider bandwidth (inverse)
        w1, w2, w3, w4 = 0.0, 1.0, 0.0, 0.0
        k = 2
        result_bandwidth = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        
        # Path with better bandwidth should come first
        expected_bandwidth = [[0, 2, 3], [0, 1, 3]]
        self.assertEqual(result_bandwidth, expected_bandwidth)
        
        # Only consider latency
        w1, w2, w3, w4 = 1.0, 0.0, 0.0, 0.0
        result_latency = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        
        # Path with better latency should come first
        expected_latency = [[0, 1, 3], [0, 2, 3]]
        self.assertEqual(result_latency, expected_latency)

    def test_edge_case_zero_values(self):
        """Test with some edges having zero values for properties."""
        n = 3
        edges = [
            (0, 1, 0, 100, 5),  # Zero latency
            (1, 2, 10, 0, 5),   # Zero bandwidth
            (0, 2, 10, 100, 0)  # Zero cost
        ]
        source = 0
        destination = 2
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 2

        # Direct path with zero cost should be preferred, 
        # path through node 1 should be invalid due to zero bandwidth
        expected = [[0, 2]]
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)

    def test_complex_network(self):
        """Test with a more complex network."""
        n = 6
        edges = [
            (0, 1, 5, 100, 10),
            (0, 2, 3, 80, 15),
            (1, 3, 7, 120, 8),
            (1, 4, 6, 90, 12),
            (2, 3, 8, 110, 9),
            (2, 4, 4, 70, 14),
            (3, 5, 6, 130, 7),
            (4, 5, 9, 150, 11)
        ]
        source = 0
        destination = 5
        min_bandwidth = 60
        max_latency = 20
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 2.0
        k = 3

        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        
        # Verify that all returned paths are valid
        for path in result:
            self.assertEqual(path[0], source)
            self.assertEqual(path[-1], destination)
            
            # Check for path continuity
            for i in range(len(path) - 1):
                found_edge = False
                for u, v, _, _, _ in edges:
                    if u == path[i] and v == path[i + 1]:
                        found_edge = True
                        break
                self.assertTrue(found_edge, f"No edge found between {path[i]} and {path[i+1]}")
        
        # There should be at most k paths
        self.assertTrue(len(result) <= k)

    def test_large_k(self):
        """Test with k larger than the number of valid paths."""
        n = 3
        edges = [(0, 1, 10, 100, 5), (1, 2, 10, 100, 5)]
        source = 0
        destination = 2
        min_bandwidth = 50
        max_latency = 25
        w1, w2, w3, w4 = 1.0, 1.0, 1.0, 1.0
        k = 10  # More than possible paths

        expected = [[0, 1, 2]]  # Only one valid path exists
        result = find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()