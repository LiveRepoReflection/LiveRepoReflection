import unittest
from network_reconstruction import reconstruct_network

def is_connected(adj_list):
    n = len(adj_list)
    visited = [False] * n
    stack = [0]
    while stack:
        current = stack.pop()
        if not visited[current]:
            visited[current] = True
            for neighbor, _ in adj_list[current]:
                if not visited[neighbor]:
                    stack.append(neighbor)
    return all(visited)

def check_symmetry(adj_list):
    n = len(adj_list)
    # Create a mapping for fast lookup: for each node u, map neighbor->latency
    mapping = [{} for _ in range(n)]
    for u in range(n):
        for v, latency in adj_list[u]:
            mapping[u][v] = latency
    for u in range(n):
        for v, latency in adj_list[u]:
            if u not in mapping[v]:
                return False
            # Allow a small numerical tolerance since latency is floating point.
            if abs(mapping[v][u] - latency) > 1e-6:
                return False
    return True

def check_sorted_neighbors(adj_list):
    for neighbors in adj_list:
        neighbor_labels = [v for v, _ in neighbors]
        if neighbor_labels != sorted(neighbor_labels):
            return False
    return True

class NetworkReconstructionTest(unittest.TestCase):
    def test_simple_network(self):
        # Basic test with 3 nodes and 2 measurements
        n = 3
        measurements = [(0, 1, 1.0), (1, 2, 2.0)]
        adj_list = reconstruct_network(n, measurements)
        # Check returned structure has n lists
        self.assertEqual(len(adj_list), n)
        # Each entry in adj_list should be a list
        for neighbors in adj_list:
            self.assertIsInstance(neighbors, list)
            for item in neighbors:
                self.assertIsInstance(item, tuple)
                self.assertEqual(len(item), 2)
                self.assertIsInstance(item[0], int)
                self.assertTrue(isinstance(item[1], float) or isinstance(item[1], int))
        # Check connectivity
        self.assertTrue(is_connected(adj_list), "The reconstructed network must be connected")
        # Check symmetry of edges
        self.assertTrue(check_symmetry(adj_list), "Edges must be bidirectional with same latency")
        # Check sorted neighbors by server label
        self.assertTrue(check_sorted_neighbors(adj_list), "Neighbors must be sorted by server label")
    
    def test_full_measurements_network(self):
        # Test with a fully measured network, even if not all edges are needed.
        n = 4
        measurements = [
            (0, 1, 1.5), (0, 2, 2.0), (0, 3, 2.5),
            (1, 2, 1.0), (1, 3, 1.2),
            (2, 3, 1.8)
        ]
        adj_list = reconstruct_network(n, measurements)
        self.assertEqual(len(adj_list), n)
        self.assertTrue(is_connected(adj_list), "The reconstructed network must be connected")
        self.assertTrue(check_symmetry(adj_list), "Edges must be bidirectional with same latency")
        self.assertTrue(check_sorted_neighbors(adj_list), "Neighbors must be sorted by server label")
    
    def test_sparse_measurements_network(self):
        # Test with sparse measurements where not all pairs are measured.
        n = 5
        measurements = [
            (0, 1, 2.1),
            (1, 2, 0.9),
            (2, 3, 3.3),
            (3, 4, 1.7)
        ]
        adj_list = reconstruct_network(n, measurements)
        self.assertEqual(len(adj_list), n)
        self.assertTrue(is_connected(adj_list), "The reconstructed network must be connected")
        self.assertTrue(check_symmetry(adj_list), "Edges must be bidirectional with same latency")
        self.assertTrue(check_sorted_neighbors(adj_list), "Neighbors must be sorted by server label")
    
    def test_no_measurements_network(self):
        # When there are no measurements provided, the solution should still return a connected network.
        # Since there is no guidance on latencies, any connected network is acceptable.
        n = 3
        measurements = []
        adj_list = reconstruct_network(n, measurements)
        self.assertEqual(len(adj_list), n)
        self.assertTrue(is_connected(adj_list), "The reconstructed network must be connected")
        self.assertTrue(check_symmetry(adj_list), "Edges must be bidirectional with same latency")
        self.assertTrue(check_sorted_neighbors(adj_list), "Neighbors must be sorted by server label")
    
    def test_network_with_alternative_paths(self):
        # Test where multiple measurements may lead to different optimal choices.
        n = 6
        measurements = [
            (0, 1, 1.0),
            (1, 2, 2.0),
            (2, 3, 1.5),
            (3, 4, 2.1),
            (4, 5, 1.1),
            (0, 5, 10.0),
            (1, 4, 3.0),
            (2, 5, 2.5)
        ]
        adj_list = reconstruct_network(n, measurements)
        self.assertEqual(len(adj_list), n)
        self.assertTrue(is_connected(adj_list), "The reconstructed network must be connected")
        self.assertTrue(check_symmetry(adj_list), "Edges must be bidirectional with same latency")
        self.assertTrue(check_sorted_neighbors(adj_list), "Neighbors must be sorted by server label")

if __name__ == '__main__':
    unittest.main()