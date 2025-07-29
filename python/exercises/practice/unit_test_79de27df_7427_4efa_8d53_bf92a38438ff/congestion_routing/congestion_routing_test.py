import unittest
from congestion_routing import find_optimal_path

class CongestionRoutingTest(unittest.TestCase):
    def test_simple_path(self):
        # Simple graph with one obvious path
        graph = {
            'A': [('B', 10, 5)],
            'B': [('C', 10, 5)],
            'C': []
        }
        self.assertEqual(find_optimal_path(graph, 'A', 'C', 0.7, 10), ['A', 'B', 'C'])

    def test_no_path(self):
        # No path from source to destination
        graph = {
            'A': [('B', 10, 5)],
            'B': [],
            'C': []
        }
        self.assertEqual(find_optimal_path(graph, 'A', 'C', 0.7, 10), [])

    def test_source_equals_destination(self):
        # Source and destination are the same
        graph = {
            'A': [('B', 10, 5)],
            'B': []
        }
        self.assertEqual(find_optimal_path(graph, 'A', 'A', 0.7, 10), ['A'])

    def test_multiple_paths_same_hops(self):
        # Multiple paths with same number of hops but different congestion
        graph = {
            'A': [('B', 10, 5), ('C', 15, 2)],  # A->B: congestion = 0.5, A->C: congestion = 0.133
            'B': [('D', 8, 6)],                  # B->D: congestion = 0.75 (congested)
            'C': [('D', 12, 9)],                 # C->D: congestion = 0.75 (congested)
            'D': []
        }
        # Both paths have same cost = 2 + (10 * 0.75) = 9.5
        path = find_optimal_path(graph, 'A', 'D', 0.7, 10)
        self.assertIn(path, [['A', 'B', 'D'], ['A', 'C', 'D']])

    def test_different_length_paths(self):
        # Shorter path with high congestion vs longer path with low congestion
        graph = {
            'A': [('B', 10, 8), ('C', 10, 2)],  # A->B: 0.8 (congested), A->C: 0.2
            'B': [('D', 10, 1)],                 # B->D: 0.1
            'C': [('E', 10, 1)],                 # C->E: 0.1
            'E': [('D', 10, 1)],                 # E->D: 0.1
            'D': []
        }
        # Path A->B->D: 2 hops + (10 * 0.8) = 10
        # Path A->C->E->D: 3 hops + (10 * 0) = 3
        self.assertEqual(find_optimal_path(graph, 'A', 'D', 0.7, 10), ['A', 'C', 'E', 'D'])

    def test_cycles(self):
        # Graph with cycles
        graph = {
            'A': [('B', 10, 5)],
            'B': [('C', 10, 5), ('A', 10, 5)],  # B can go back to A
            'C': [('D', 10, 5), ('B', 10, 5)],  # C can go back to B
            'D': []
        }
        self.assertEqual(find_optimal_path(graph, 'A', 'D', 0.7, 10), ['A', 'B', 'C', 'D'])

    def test_large_graph(self):
        # A larger graph to test efficiency
        graph = {}
        # Create a linear graph with 1000 nodes
        for i in range(999):
            node = f'N{i}'
            next_node = f'N{i+1}'
            graph[node] = [(next_node, 10, 5)]
        graph[f'N999'] = []
        
        # Verify the algorithm can handle a large graph efficiently
        path = find_optimal_path(graph, 'N0', 'N999', 0.7, 10)
        self.assertEqual(len(path), 1000)  # 1000 nodes from N0 to N999
        for i in range(1000):
            self.assertEqual(path[i], f'N{i}')

    def test_varying_congestion_thresholds(self):
        # Test how different congestion thresholds affect path selection
        graph = {
            'A': [('B', 10, 6), ('C', 10, 2)],  # A->B: 0.6, A->C: 0.2
            'B': [('D', 10, 6)],                 # B->D: 0.6
            'C': [('D', 10, 8)],                 # C->D: 0.8
            'D': []
        }
        
        # With threshold 0.7, A->C->D has congestion on C->D, while A->B->D has none
        # Path A->B->D: 2 hops + (10 * 0) = 2
        # Path A->C->D: 2 hops + (10 * 0.8) = 10
        self.assertEqual(find_optimal_path(graph, 'A', 'D', 0.7, 10), ['A', 'B', 'D'])
        
        # With threshold 0.5, both paths have congestion
        # Path A->B->D: 2 hops + (10 * (0.6 + 0.6)) = 14
        # Path A->C->D: 2 hops + (10 * 0.8) = 10
        self.assertEqual(find_optimal_path(graph, 'A', 'D', 0.5, 10), ['A', 'C', 'D'])

    def test_penalty_factor_influence(self):
        # Test how different penalty factors influence path selection
        graph = {
            'A': [('B', 10, 8), ('C', 10, 5)],  # A->B: 0.8 (high), A->C: 0.5 (medium)
            'B': [('D', 10, 2)],                 # B->D: 0.2 (low)
            'C': [('E', 10, 2)],                 # C->E: 0.2 (low)
            'E': [('F', 10, 2)],                 # E->F: 0.2 (low)
            'F': [('D', 10, 2)],                 # F->D: 0.2 (low)
            'D': []
        }
        
        # With threshold 0.7 and low penalty factor 2
        # Path A->B->D: 2 hops + (2 * 0.8) = 3.6
        # Path A->C->E->F->D: 4 hops + (2 * 0) = 4
        self.assertEqual(find_optimal_path(graph, 'A', 'D', 0.7, 2), ['A', 'B', 'D'])
        
        # With threshold 0.7 and high penalty factor 20
        # Path A->B->D: 2 hops + (20 * 0.8) = 18
        # Path A->C->E->F->D: 4 hops + (20 * 0) = 4
        self.assertEqual(find_optimal_path(graph, 'A', 'D', 0.7, 20), ['A', 'C', 'E', 'F', 'D'])

    def test_isolated_nodes(self):
        # Test with isolated nodes
        graph = {
            'A': [('B', 10, 5)],
            'B': [],
            'C': [],  # Isolated node
            'D': []   # Isolated node
        }
        self.assertEqual(find_optimal_path(graph, 'A', 'C', 0.7, 10), [])
        self.assertEqual(find_optimal_path(graph, 'C', 'D', 0.7, 10), [])

    def test_missing_nodes(self):
        # Test with nodes that don't exist in the graph
        graph = {
            'A': [('B', 10, 5)],
            'B': []
        }
        self.assertEqual(find_optimal_path(graph, 'A', 'Z', 0.7, 10), [])
        self.assertEqual(find_optimal_path(graph, 'Z', 'A', 0.7, 10), [])

if __name__ == '__main__':
    unittest.main()