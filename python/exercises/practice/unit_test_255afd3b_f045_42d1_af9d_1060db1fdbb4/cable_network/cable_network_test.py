import unittest
from cable_network import find_min_latency_path


class CableNetworkTest(unittest.TestCase):
    def test_simple_path(self):
        # A simple linear path with enough bandwidth
        nodes = 3
        edges = [(1, 2, 10, 5), (2, 3, 8, 10)]
        source = 1
        destination = 3
        min_bandwidth = 8
        
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, 15)  # Total latency: 5 + 10 = 15

    def test_multiple_paths(self):
        # Multiple possible paths, one with higher bandwidth but higher latency
        nodes = 4
        edges = [
            (1, 2, 10, 5),
            (2, 4, 10, 10),
            (1, 3, 5, 3),
            (3, 4, 5, 3)
        ]
        source = 1
        destination = 4
        min_bandwidth = 5
        
        # Path 1->2->4 has bandwidth 10, latency 15
        # Path 1->3->4 has bandwidth 5, latency 6
        # Both satisfy the bandwidth requirement, but the second has lower latency
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, 6)

    def test_insufficient_bandwidth(self):
        # No path with sufficient bandwidth
        nodes = 3
        edges = [(1, 2, 5, 5), (2, 3, 4, 10)]
        source = 1
        destination = 3
        min_bandwidth = 6
        
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, -1)

    def test_disconnected_graph(self):
        # No path between source and destination
        nodes = 4
        edges = [(1, 2, 10, 5), (3, 4, 10, 5)]
        source = 1
        destination = 4
        min_bandwidth = 5
        
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, -1)

    def test_direct_edge(self):
        # Direct edge between source and destination
        nodes = 5
        edges = [
            (1, 2, 10, 5),
            (2, 3, 10, 5),
            (3, 4, 10, 5),
            (1, 4, 8, 12)
        ]
        source = 1
        destination = 4
        min_bandwidth = 8
        
        # Path 1->2->3->4 has bandwidth 10, latency 15
        # Path 1->4 has bandwidth 8, latency 12
        # Both satisfy the bandwidth requirement, but the direct path has lower latency
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, 12)

    def test_large_graph(self):
        # Test with a larger graph structure
        nodes = 8
        edges = [
            (1, 2, 20, 5),
            (2, 3, 15, 5),
            (3, 6, 10, 10),
            (6, 8, 25, 5),
            (1, 4, 30, 8),
            (4, 5, 20, 7),
            (5, 8, 15, 10),
            (4, 7, 25, 6),
            (7, 8, 20, 5),
            (1, 5, 10, 25)
        ]
        source = 1
        destination = 8
        min_bandwidth = 15
        
        # Path 1->4->7->8 has bandwidth min(30,25,20) = 20, latency 8+6+5 = 19
        # Path 1->2->3->6->8 has bandwidth min(20,15,10,25) = 10, latency 5+5+10+5 = 25
        # Path 1->4->5->8 has bandwidth min(30,20,15) = 15, latency 8+7+10 = 25
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, 19)

    def test_equal_latency_paths(self):
        # Test where multiple paths have the same latency
        nodes = 4
        edges = [
            (1, 2, 20, 5),
            (2, 4, 20, 5),
            (1, 3, 15, 4),
            (3, 4, 15, 6)
        ]
        source = 1
        destination = 4
        min_bandwidth = 15
        
        # Path 1->2->4 has bandwidth 20, latency 10
        # Path 1->3->4 has bandwidth 15, latency 10
        # Both are valid, return any one
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, 10)

    def test_same_source_destination(self):
        # Source is the same as destination
        nodes = 4
        edges = [
            (1, 2, 20, 5),
            (2, 3, 20, 5),
            (3, 4, 20, 5)
        ]
        source = 2
        destination = 2
        min_bandwidth = 10
        
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, 0)  # No latency to stay at the same node

    def test_missing_nodes(self):
        # Test with node IDs that are not consecutive
        nodes = 5  # Actual nodes are 1,3,5,7,9
        edges = [
            (1, 3, 20, 5),
            (3, 5, 15, 5),
            (5, 7, 10, 5),
            (7, 9, 10, 5)
        ]
        source = 1
        destination = 9
        min_bandwidth = 10
        
        result = find_min_latency_path(nodes, edges, source, destination, min_bandwidth)
        self.assertEqual(result, 20)  # Total latency: 5+5+5+5 = 20

if __name__ == '__main__':
    unittest.main()