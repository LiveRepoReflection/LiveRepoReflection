import unittest
from network_pathfinder import find_optimal_path

class NetworkPathfinderTest(unittest.TestCase):
    def test_simple_path(self):
        # Simple path with only one possible route
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (2, 1)}},
            2: {'processing_power': 15, 'security_level': 8, 'edges': {3: (3, 1)}},
            3: {'processing_power': 20, 'security_level': 10, 'edges': {}}
        }
        self.assertEqual(find_optimal_path(graph, 1, 3), [1, 2, 3])

    def test_multiple_paths(self):
        # Graph with multiple possible paths
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (2, 1), 3: (5, 2)}},
            2: {'processing_power': 15, 'security_level': 8, 'edges': {4: (3, 1)}},
            3: {'processing_power': 8, 'security_level': 3, 'edges': {4: (1, 3)}},
            4: {'processing_power': 20, 'security_level': 10, 'edges': {}}
        }
        # Path [1,2,4] score: 15+8-2-1-3-1 = 16
        # Path [1,3,4] score: 8+3-5-2-1-3 = 0
        # [1,2,4] has a higher score
        self.assertEqual(find_optimal_path(graph, 1, 4), [1, 2, 4])
        
    def test_optimal_path_with_tradeoffs(self):
        # Test where a longer path might be better due to better server attributes
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (1, 1), 3: (2, 1)}},
            2: {'processing_power': 5, 'security_level': 3, 'edges': {4: (1, 1)}},
            3: {'processing_power': 15, 'security_level': 10, 'edges': {5: (1, 1)}},
            4: {'processing_power': 5, 'security_level': 3, 'edges': {6: (1, 1)}},
            5: {'processing_power': 15, 'security_level': 10, 'edges': {6: (1, 1)}},
            6: {'processing_power': 20, 'security_level': 15, 'edges': {}}
        }
        # Path [1,2,4,6] score: 5+3+5+3-1-1-1-1-1-1 = 5
        # Path [1,3,5,6] score: 15+10+15+10-2-1-1-1-1-1 = 44
        # [1,3,5,6] has a higher score despite potentially higher latency
        self.assertEqual(find_optimal_path(graph, 1, 6), [1, 3, 5, 6])

    def test_no_path(self):
        # Test when no path exists
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (2, 1)}},
            2: {'processing_power': 15, 'security_level': 8, 'edges': {}},
            3: {'processing_power': 20, 'security_level': 10, 'edges': {}}
        }
        self.assertIsNone(find_optimal_path(graph, 1, 3))

    def test_source_equals_destination(self):
        # Test when source equals destination
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (2, 1)}},
            2: {'processing_power': 15, 'security_level': 8, 'edges': {}}
        }
        self.assertEqual(find_optimal_path(graph, 1, 1), [1])

    def test_cycle_handling(self):
        # Test with cycles in the graph
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (2, 1)}},
            2: {'processing_power': 15, 'security_level': 8, 'edges': {3: (3, 1), 1: (1, 1)}},
            3: {'processing_power': 20, 'security_level': 10, 'edges': {4: (1, 1)}},
            4: {'processing_power': 25, 'security_level': 12, 'edges': {}}
        }
        # The path should not include cycles unless beneficial
        self.assertEqual(find_optimal_path(graph, 1, 4), [1, 2, 3, 4])

    def test_tie_breaking(self):
        # Test tie breaking by choosing the path with fewer hops
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (1, 1), 3: (1, 1)}},
            2: {'processing_power': 20, 'security_level': 10, 'edges': {4: (1, 1)}},
            3: {'processing_power': 10, 'security_level': 5, 'edges': {5: (1, 1)}},
            4: {'processing_power': 10, 'security_level': 5, 'edges': {6: (1, 1)}},
            5: {'processing_power': 20, 'security_level': 10, 'edges': {6: (1, 1)}},
            6: {'processing_power': 15, 'security_level': 8, 'edges': {}}
        }
        # Path [1,2,4,6] and [1,3,5,6] have the same score but different hop counts
        # [1,2,4,6] has a total score of 20+10+10+5-1-1-1-1-1-1 = 39
        # [1,3,5,6] has a total score of 10+5+20+10-1-1-1-1-1-1 = 39
        # Both paths have the same score, so the one with fewer hops should be chosen
        # But both have the same number of hops too, so either could be returned
        path = find_optimal_path(graph, 1, 6)
        self.assertIn(path, [[1, 2, 4, 6], [1, 3, 5, 6]])
        self.assertEqual(len(path), 4)  # Either way, should have 4 nodes

    def test_large_graph(self):
        # Create a larger graph to test performance and correctness
        graph = {}
        # Create a linear graph with 1000 nodes
        for i in range(1, 1000):
            graph[i] = {
                'processing_power': i % 20 + 5,
                'security_level': i % 15 + 3,
                'edges': {i+1: (i % 5 + 1, i % 4 + 1)}
            }
        # Add the last node
        graph[1000] = {
            'processing_power': 25,
            'security_level': 15,
            'edges': {}
        }
        
        # Add some shortcuts to create multiple paths
        for i in range(1, 900, 100):
            graph[i]['edges'][i+10] = (3, 2)
        
        # The optimal path should not be simply the shortest in terms of hops
        path = find_optimal_path(graph, 1, 1000)
        self.assertIsNotNone(path)
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], 1)
        self.assertEqual(path[-1], 1000)

    def test_complex_network_with_variations(self):
        # Test with a more complex network that has significant variations in server attributes
        graph = {}
        # Create a grid-like graph with varying attributes
        for i in range(1, 21):
            for j in range(1, 21):
                node_id = (i-1) * 20 + j
                graph[node_id] = {
                    'processing_power': (i + j) % 30 + 5,
                    'security_level': (i * j) % 20 + 3,
                    'edges': {}
                }
                # Add horizontal edges
                if j < 20:
                    graph[node_id]['edges'][node_id + 1] = ((i + j) % 5 + 1, (i * j) % 4 + 1)
                # Add vertical edges
                if i < 20:
                    graph[node_id]['edges'][node_id + 20] = ((i + j) % 6 + 1, (i * j) % 5 + 1)
                # Add some diagonal edges for complexity
                if i < 20 and j < 20:
                    graph[node_id]['edges'][node_id + 21] = ((i * j) % 4 + 1, (i + j) % 3 + 1)
        
        # Test finding path from top left to bottom right
        path = find_optimal_path(graph, 1, 400)
        self.assertIsNotNone(path)
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], 1)
        self.assertEqual(path[-1], 400)
        
    def test_disconnected_graph(self):
        # Test with disconnected components in the graph
        graph = {
            1: {'processing_power': 10, 'security_level': 5, 'edges': {2: (2, 1)}},
            2: {'processing_power': 15, 'security_level': 8, 'edges': {3: (3, 1)}},
            3: {'processing_power': 20, 'security_level': 10, 'edges': {}},
            4: {'processing_power': 25, 'security_level': 12, 'edges': {5: (1, 1)}},
            5: {'processing_power': 30, 'security_level': 15, 'edges': {}}
        }
        self.assertEqual(find_optimal_path(graph, 1, 3), [1, 2, 3])
        self.assertIsNone(find_optimal_path(graph, 1, 5))

if __name__ == '__main__':
    unittest.main()