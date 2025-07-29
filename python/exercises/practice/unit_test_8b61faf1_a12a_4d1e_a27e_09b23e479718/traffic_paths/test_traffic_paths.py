import unittest
from traffic_paths import optimize_multi_source_paths

class TestTrafficPaths(unittest.TestCase):
    
    def test_simple_graph_no_congestion(self):
        # Test with a simple graph with no congestion
        graph = {
            'A': [('B', 10), ('C', 15)],
            'B': [('D', 12), ('E', 15)],
            'C': [('F', 10)],
            'D': [('F', 2)],
            'E': [('F', 5)],
            'F': []
        }
        sources = ['A', 'B']
        T = 3600  # 1 hour
        vehicle_rate = 0
        
        # Function that always returns 1 (no congestion)
        def no_congestion(time, flow):
            return 1
        
        result = optimize_multi_source_paths(graph, sources, T, no_congestion, vehicle_rate)
        
        expected = {
            'A': {'A': 0, 'B': 10, 'C': 15, 'D': 22, 'E': 25, 'F': 24},
            'B': {'A': float('inf'), 'B': 0, 'C': float('inf'), 'D': 12, 'E': 15, 'F': 14}
        }
        
        # Check all path lengths
        for source in expected:
            self.assertIn(source, result)
            for dest in expected[source]:
                self.assertIn(dest, result[source])
                self.assertAlmostEqual(expected[source][dest], result[source][dest], 
                                      msg=f"Path from {source} to {dest} incorrect")

    def test_with_congestion(self):
        # Test with a simple graph with congestion
        graph = {
            'A': [('B', 10), ('C', 15)],
            'B': [('D', 12), ('E', 15)],
            'C': [('F', 10)],
            'D': [('F', 2)],
            'E': [('F', 5)],
            'F': []
        }
        sources = ['A', 'B']
        T = 3600  # 1 hour
        vehicle_rate = 0.1  # vehicles/second
        
        # Simple linear congestion model
        def congestion_factor(time, flow):
            return 1 + (flow * 0.01) if flow > 0 else 1
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        # We expect congestion to affect travel times
        # The actual values may vary depending on implementation details
        # We'll just do basic checks that the structure is correct
        for source in sources:
            self.assertIn(source, result)
            for node in graph:
                self.assertIn(node, result[source])
                # Each node should have a travel time >= 0 or infinity if unreachable
                self.assertTrue(result[source][node] >= 0 or result[source][node] == float('inf'))

    def test_disconnected_graph(self):
        # Test with a disconnected graph
        graph = {
            'A': [('B', 5)],
            'B': [('A', 5)],
            'C': [('D', 10)],
            'D': [('C', 10)]
        }
        sources = ['A', 'C']
        T = 3600
        vehicle_rate = 0.1
        
        def congestion_factor(time, flow):
            return 1
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        expected = {
            'A': {'A': 0, 'B': 5, 'C': float('inf'), 'D': float('inf')},
            'C': {'A': float('inf'), 'B': float('inf'), 'C': 0, 'D': 10}
        }
        
        for source in expected:
            self.assertIn(source, result)
            for dest in expected[source]:
                self.assertIn(dest, result[source])
                self.assertEqual(expected[source][dest], result[source][dest], 
                               msg=f"Path from {source} to {dest} incorrect")

    def test_complex_graph(self):
        # Test with a more complex graph
        graph = {
            'A': [('B', 5), ('C', 10), ('D', 15)],
            'B': [('A', 5), ('C', 3), ('E', 12)],
            'C': [('A', 10), ('B', 3), ('D', 2), ('E', 7), ('F', 8)],
            'D': [('A', 15), ('C', 2), ('F', 6)],
            'E': [('B', 12), ('C', 7), ('F', 4)],
            'F': [('C', 8), ('D', 6), ('E', 4), ('G', 3)],
            'G': [('F', 3)]
        }
        sources = ['A', 'E']
        T = 7200  # 2 hours
        vehicle_rate = 0.2  # vehicles/second
        
        def congestion_factor(time, flow):
            return 1 + 0.005 * flow
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        # Verify all nodes are reachable from all sources
        for source in sources:
            self.assertIn(source, result)
            for node in graph:
                self.assertIn(node, result[source])
                # Each node should be reachable (except possibly from itself)
                if source != node:
                    self.assertTrue(result[source][node] > 0, 
                                 msg=f"Node {node} should be reachable from {source}")

    def test_time_dependent_congestion(self):
        # Test with time-dependent congestion
        graph = {
            'A': [('B', 10), ('C', 20)],
            'B': [('D', 15)],
            'C': [('D', 10)],
            'D': []
        }
        sources = ['A']
        T = 3600  # 1 hour
        vehicle_rate = 0.5  # vehicles/second
        
        # Congestion increases with time
        def congestion_factor(time, flow):
            return 1 + (time / 3600) * 0.5  # Increases by 50% over an hour
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        # Path lengths should be affected by time-dependent congestion
        # But we can't predict the exact values without knowing the implementation details
        # So we just check that the paths exist
        for source in sources:
            self.assertIn(source, result)
            for node in graph:
                self.assertIn(node, result[source])
    
    def test_single_node_graph(self):
        # Test with a graph containing only one node
        graph = {'A': []}
        sources = ['A']
        T = 3600
        vehicle_rate = 0.1
        
        def congestion_factor(time, flow):
            return 1
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        expected = {'A': {'A': 0}}
        self.assertEqual(expected, result)

    def test_empty_sources(self):
        # Test with empty sources list
        graph = {
            'A': [('B', 10)],
            'B': []
        }
        sources = []
        T = 3600
        vehicle_rate = 0.1
        
        def congestion_factor(time, flow):
            return 1
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        # Should return an empty dictionary
        self.assertEqual({}, result)

    def test_cyclic_graph(self):
        # Test with a graph containing cycles
        graph = {
            'A': [('B', 5)],
            'B': [('C', 5)],
            'C': [('A', 5)]
        }
        sources = ['A']
        T = 3600
        vehicle_rate = 0.1
        
        def congestion_factor(time, flow):
            return 1
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        expected = {
            'A': {'A': 0, 'B': 5, 'C': 10}
        }
        
        for source in expected:
            self.assertIn(source, result)
            for dest in expected[source]:
                self.assertIn(dest, result[source])
                self.assertEqual(expected[source][dest], result[source][dest],
                               msg=f"Path from {source} to {dest} incorrect")

    def test_parallel_edges(self):
        # Test with multiple paths between nodes
        # This is represented as multiple entries in the adjacency list
        graph = {
            'A': [('B', 10), ('B', 8), ('C', 15)],  # Two paths from A to B
            'B': [('C', 5)],
            'C': []
        }
        sources = ['A']
        T = 3600
        vehicle_rate = 0.1
        
        def congestion_factor(time, flow):
            return 1
        
        result = optimize_multi_source_paths(graph, sources, T, congestion_factor, vehicle_rate)
        
        # The algorithm should pick the shortest path from A to B
        self.assertIn('A', result)
        self.assertIn('B', result['A'])
        self.assertEqual(8, result['A']['B'], "Should use the shortest path from A to B")

if __name__ == '__main__':
    unittest.main()