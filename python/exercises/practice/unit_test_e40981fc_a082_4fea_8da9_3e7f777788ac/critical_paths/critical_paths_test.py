import unittest
from critical_paths import find_critical_paths

class CriticalPathsTest(unittest.TestCase):
    def test_basic_example(self):
        graph = {
            1: [(2, 50), (3, 100)],
            2: [(4, 20)],
            3: [(4, 80)],
            4: []
        }

        traffic = {
            (1, 2): 1000,
            (1, 3): 500,
            (2, 4): 2000,
            (3, 4): 750
        }

        result = find_critical_paths(graph, traffic, 2)
        self.assertEqual(len(result), 2)
        
        # Verify structure of result
        for path in result:
            self.assertEqual(len(path), 3)
            self.assertIsInstance(path[0], int)  # source_id
            self.assertIsInstance(path[1], int)  # destination_id
            self.assertIsInstance(path[2], (int, float))  # criticality score
        
        # Verify criticality scores are in descending order
        self.assertGreaterEqual(result[0][2], result[1][2])

    def test_complete_graph(self):
        graph = {
            1: [(2, 10), (3, 20), (4, 30)],
            2: [(1, 10), (3, 40), (4, 50)],
            3: [(1, 20), (2, 40), (4, 60)],
            4: [(1, 30), (2, 50), (3, 60)]
        }
        
        traffic = {
            (1, 2): 100, (1, 3): 200, (1, 4): 300,
            (2, 1): 150, (2, 3): 250, (2, 4): 350,
            (3, 1): 400, (3, 2): 450, (3, 4): 500,
            (4, 1): 550, (4, 2): 600, (4, 3): 650
        }
        
        result = find_critical_paths(graph, traffic, 5)
        self.assertEqual(len(result), 5)
        
        # Check if critical paths are sorted by criticality score
        for i in range(len(result) - 1):
            self.assertGreaterEqual(result[i][2], result[i+1][2])

    def test_K_larger_than_paths(self):
        graph = {
            1: [(2, 10)],
            2: []
        }
        
        traffic = {
            (1, 2): 100
        }
        
        result = find_critical_paths(graph, traffic, 5)
        self.assertEqual(len(result), 1)  # Should return only the one available path

    def test_disconnected_graph(self):
        graph = {
            1: [(2, 50)],
            2: [],
            3: [(4, 30)],
            4: [],
            5: []
        }
        
        traffic = {
            (1, 2): 1000,
            (3, 4): 2000
        }
        
        result = find_critical_paths(graph, traffic, 2)
        self.assertEqual(len(result), 2)
        
        # Path (3,4) should have higher criticality due to higher traffic
        self.assertEqual(result[0][0], 3)
        self.assertEqual(result[0][1], 4)

    def test_cyclic_graph(self):
        graph = {
            1: [(2, 50)],
            2: [(3, 20)],
            3: [(1, 30)]
        }
        
        traffic = {
            (1, 2): 100,
            (2, 3): 200,
            (3, 1): 300
        }
        
        result = find_critical_paths(graph, traffic, 3)
        self.assertEqual(len(result), 3)

    def test_incomplete_traffic_data(self):
        graph = {
            1: [(2, 10), (3, 20)],
            2: [(4, 30)],
            3: [(4, 40)],
            4: []
        }
        
        # Missing traffic data for (3, 4)
        traffic = {
            (1, 2): 100,
            (1, 3): 200,
            (2, 4): 300
        }
        
        result = find_critical_paths(graph, traffic, 3)
        self.assertEqual(len(result), 3)
        
        # Check if all edges in graph are accounted for in result
        edge_set = {(path[0], path[1]) for path in result}
        self.assertIn((1, 2), edge_set)
        self.assertIn((1, 3), edge_set)
        self.assertIn((2, 4), edge_set)

    def test_tie_breaking_by_latency(self):
        graph = {
            1: [(2, 100), (3, 50)],
            2: [],
            3: []
        }
        
        # Same traffic for both paths
        traffic = {
            (1, 2): 1000,
            (1, 3): 1000
        }
        
        result = find_critical_paths(graph, traffic, 2)
        
        # Path with higher latency should come first
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], 2)
        self.assertEqual(result[1][0], 1)
        self.assertEqual(result[1][1], 3)

    def test_tie_breaking_by_traffic(self):
        graph = {
            1: [(2, 50), (3, 50)],
            2: [],
            3: []
        }
        
        # Same latency for both paths but different traffic
        traffic = {
            (1, 2): 2000,
            (1, 3): 1000
        }
        
        result = find_critical_paths(graph, traffic, 2)
        
        # Path with higher traffic should come first
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], 2)
        self.assertEqual(result[1][0], 1)
        self.assertEqual(result[1][1], 3)

    def test_large_graph_performance(self):
        # Create a larger graph to test performance
        graph = {}
        traffic = {}
        
        # Create a graph with 1000 nodes and ~3000 edges
        for i in range(1, 1001):
            neighbors = []
            # Each node connects to up to 3 other nodes
            for j in range(1, 4):
                if i + j <= 1000:
                    latency = (i * j) % 100 + 1  # Some latency value
                    neighbors.append((i + j, latency))
                    traffic[(i, i + j)] = (i * j) % 1000 + 1  # Some traffic value
            graph[i] = neighbors
        
        # Should handle large graphs efficiently
        result = find_critical_paths(graph, traffic, 10)
        self.assertEqual(len(result), 10)

    def test_empty_graph(self):
        graph = {}
        traffic = {}
        
        result = find_critical_paths(graph, traffic, 5)
        self.assertEqual(len(result), 0)  # Should return empty list

    def test_graph_with_zero_traffic(self):
        graph = {
            1: [(2, 50), (3, 100)],
            2: [],
            3: []
        }
        
        traffic = {
            (1, 2): 0,
            (1, 3): 0
        }
        
        result = find_critical_paths(graph, traffic, 2)
        self.assertEqual(len(result), 2)
        
        # Even with zero traffic, paths should be returned and scored
        # based on the scoring function's handling of zero traffic

if __name__ == '__main__':
    unittest.main()