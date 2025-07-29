import unittest
from quantum_maze import most_probable_path

class QuantumMazeTest(unittest.TestCase):
    def test_simple_path_no_entanglement(self):
        # A simple path from 0 to 2: 0 -> 1 -> 2 with probability 0.5 * 0.7 = 0.35
        edges = [(0, 1, 0.5), (1, 2, 0.7), (0, 3, 0.5), (3, 2, 0.3)]
        entangled_pairs = []
        start, end = 0, 2
        
        expected = 0.35
        result = most_probable_path(3, edges, entangled_pairs, start, end)
        self.assertAlmostEqual(expected, result, delta=1e-9)

    def test_no_path_exists(self):
        # No path from 0 to 4
        edges = [(0, 1, 1.0), (1, 2, 0.5), (2, 3, 1.0)]
        entangled_pairs = []
        start, end = 0, 4
        
        expected = 0.0
        result = most_probable_path(5, edges, entangled_pairs, start, end)
        self.assertAlmostEqual(expected, result, delta=1e-9)

    def test_multiple_paths(self):
        # Three paths from 0 to 3:
        # 0 -> 1 -> 3 with probability 0.3 * 0.6 = 0.18
        # 0 -> 2 -> 3 with probability 0.7 * 0.4 = 0.28
        # 0 -> 2 -> 1 -> 3 with probability 0.7 * 0.6 * 0.6 = 0.252
        # Most probable path is 0 -> 2 -> 3 with probability 0.28
        edges = [
            (0, 1, 0.3), (0, 2, 0.7),
            (1, 3, 0.6), (1, 0, 0.4),
            (2, 3, 0.4), (2, 1, 0.6),
            (3, 0, 1.0)
        ]
        entangled_pairs = []
        start, end = 0, 3
        
        expected = 0.28
        result = most_probable_path(4, edges, entangled_pairs, start, end)
        self.assertAlmostEqual(expected, result, delta=1e-9)

    def test_simple_entanglement(self):
        # When 0 is visited, the edge from 2 to 3 has probability multiplied by 2.0
        # Then normalize probabilities from node 2
        # Path 0 -> 1 -> 3: 0.6 * 0.7 = 0.42
        # Path 0 -> 2 -> 3: 0.4 * (0.3*2.0)/(0.3*2.0 + 0.7) = 0.4 * 0.46 = 0.184
        # Most probable path is 0 -> 1 -> 3 with probability 0.42
        edges = [
            (0, 1, 0.6), (0, 2, 0.4),
            (1, 3, 0.7), (1, 0, 0.3),
            (2, 3, 0.3), (2, 0, 0.7)
        ]
        entangled_pairs = [(0, 2, {3: 2.0})]
        start, end = 0, 3
        
        expected = 0.42
        result = most_probable_path(4, edges, entangled_pairs, start, end)
        self.assertAlmostEqual(expected, result, delta=1e-9)

    def test_complex_entanglement(self):
        # Multiple entangled pairs with different coupling factors
        edges = [
            (0, 1, 0.5), (0, 2, 0.5),
            (1, 3, 0.7), (1, 4, 0.3),
            (2, 3, 0.4), (2, 5, 0.6),
            (3, 6, 1.0),
            (4, 6, 0.8), (4, 5, 0.2),
            (5, 6, 0.9), (5, 4, 0.1)
        ]
        # When 1 is visited, edge probabilities from 5 change
        # When 2 is visited, edge probabilities from 4 change
        entangled_pairs = [
            (1, 5, {6: 0.5, 4: 3.0}),  # When 1 is visited, edges from 5 to 6 and 4 change
            (2, 4, {6: 1.5, 5: 0.8})   # When 2 is visited, edges from 4 to 6 and 5 change
        ]
        start, end = 0, 6
        
        # Complex calculation needed for expected value
        # One possible path calculation:
        # 0 -> 1 -> 3 -> 6: 0.5 * 0.7 * 1.0 = 0.35
        # (When node 1 is visited, it affects probabilities from node 5, 
        # but this doesn't affect this particular path)
        # This may not be the most probable path; the test implementation should calculate it
        
        result = most_probable_path(7, edges, entangled_pairs, start, end)
        self.assertTrue(0.0 < result <= 1.0)  # Sanity check

    def test_zero_coupling_factor(self):
        # When 0 is visited, the edge from 2 to 3 becomes impossible (coupling factor = 0)
        edges = [
            (0, 1, 0.5), (0, 2, 0.5),
            (1, 3, 0.6), (1, 0, 0.4),
            (2, 3, 0.4), (2, 0, 0.6)
        ]
        entangled_pairs = [(0, 2, {3: 0.0})]
        start, end = 0, 3
        
        # Only path is now 0 -> 1 -> 3 with probability 0.5 * 0.6 = 0.3
        expected = 0.3
        result = most_probable_path(4, edges, entangled_pairs, start, end)
        self.assertAlmostEqual(expected, result, delta=1e-9)

    def test_bidirectional_entanglement(self):
        # Both nodes in an entangled pair affect each other
        edges = [
            (0, 1, 0.6), (0, 2, 0.4),
            (1, 3, 0.7), (1, 0, 0.3),
            (2, 3, 0.3), (2, 0, 0.7),
            (3, 4, 1.0)
        ]
        entangled_pairs = [
            (1, 2, {3: 2.0}),  # When 1 is visited, edge from 2 to 3 changes
            (2, 1, {3: 0.5})   # When 2 is visited, edge from 1 to 3 changes
        ]
        start, end = 0, 4
        
        result = most_probable_path(5, edges, entangled_pairs, start, end)
        self.assertTrue(0.0 < result <= 1.0)

    def test_large_maze(self):
        # Create a larger maze to test efficiency
        N = 100
        edges = []
        # Create a linear path with probability 0.9 at each step
        for i in range(N-1):
            edges.append((i, i+1, 0.9))
            if i > 0:  # Add some backward edges
                edges.append((i, i-1, 0.1))
        
        # Add some entangled pairs
        entangled_pairs = []
        for i in range(0, N-10, 10):
            entangled_pairs.append((i, i+5, {i+6: 1.2}))
        
        start, end = 0, N-1
        
        result = most_probable_path(N, edges, entangled_pairs, start, end)
        self.assertTrue(0.0 < result <= 1.0)

    def test_cycle_with_entanglement(self):
        # Test maze with cycles and entanglement
        edges = [
            (0, 1, 0.7), (0, 2, 0.3),
            (1, 3, 0.6), (1, 2, 0.4),
            (2, 3, 0.5), (2, 0, 0.5),
            (3, 0, 0.4), (3, 4, 0.6),
            (4, 0, 1.0)
        ]
        entangled_pairs = [(0, 3, {4: 2.0})]
        start, end = 0, 4
        
        result = most_probable_path(5, edges, entangled_pairs, start, end)
        self.assertTrue(0.0 < result <= 1.0)

    def test_entangled_node_with_no_outgoing_edges(self):
        # Test the case where an entangled node has no outgoing edges
        edges = [
            (0, 1, 0.5), (0, 2, 0.5),
            (1, 3, 1.0),
            (2, 4, 1.0)
            # Node 5 has no outgoing edges
        ]
        entangled_pairs = [(0, 5, {})]  # Empty couplings dict as 5 has no outgoing edges
        start, end = 0, 3
        
        expected = 0.5  # Path 0 -> 1 -> 3
        result = most_probable_path(6, edges, entangled_pairs, start, end)
        self.assertAlmostEqual(expected, result, delta=1e-9)

if __name__ == "__main__":
    unittest.main()