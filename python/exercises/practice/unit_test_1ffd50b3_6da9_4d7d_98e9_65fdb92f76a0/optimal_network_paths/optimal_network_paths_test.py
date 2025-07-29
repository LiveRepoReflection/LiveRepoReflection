import unittest
from optimal_network_paths import find_optimal_path

class OptimalNetworkPathsTest(unittest.TestCase):
    def test_simple_path(self):
        # A simple linear path
        node_capacities = [10, 15, 20, 12, 18]
        connections = [(0, 1, 5), (1, 2, 10), (0, 3, 8), (3, 4, 7), (2, 4, 3)]
        source = 0
        destination = 4
        data_size = 100
        latency_budget = 30
        
        expected = [0, 3, 4]
        result = find_optimal_path(5, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(result, expected)
    
    def test_direct_path(self):
        # Direct connection between source and destination
        node_capacities = [10, 20]
        connections = [(0, 1, 5)]
        source = 0
        destination = 1
        data_size = 100
        latency_budget = 10
        
        expected = [0, 1]
        result = find_optimal_path(2, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(result, expected)
    
    def test_same_source_destination(self):
        # Source and destination are the same
        node_capacities = [10, 15, 20]
        connections = [(0, 1, 5), (1, 2, 7)]
        source = 1
        destination = 1
        data_size = 50
        latency_budget = 20
        
        expected = [1]
        result = find_optimal_path(3, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(result, expected)
    
    def test_no_valid_path(self):
        # No valid path within latency budget
        node_capacities = [10, 15, 20, 12, 18]
        connections = [(0, 1, 5), (1, 2, 10), (0, 3, 8), (3, 4, 7), (2, 4, 3)]
        source = 0
        destination = 4
        data_size = 100
        latency_budget = 10  # Too restrictive
        
        expected = []
        result = find_optimal_path(5, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(result, expected)
    
    def test_disconnected_graph(self):
        # No path exists because graph is disconnected
        node_capacities = [10, 15, 20, 12, 18]
        connections = [(0, 1, 5), (1, 2, 10), (3, 4, 7)]  # No connection between 0-2-3-4 group and 3-4 group
        source = 0
        destination = 4
        data_size = 100
        latency_budget = 50
        
        expected = []
        result = find_optimal_path(5, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(result, expected)
    
    def test_multiple_paths_same_cost(self):
        # Multiple paths with same cost, should choose one with fewer hops
        node_capacities = [10, 10, 10, 10]
        connections = [(0, 1, 5), (1, 3, 5), (0, 2, 5), (2, 3, 5)]
        source = 0
        destination = 3
        data_size = 10
        latency_budget = 20
        
        # Both [0,1,3] and [0,2,3] have same latency (10) and processing cost (2),
        # but we expect shortest path in terms of hops
        result = find_optimal_path(4, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(len(result), 3)  # Should be a path with 3 nodes
        self.assertEqual(result[0], 0)    # Should start with source
        self.assertEqual(result[-1], 3)   # Should end with destination
    
    def test_complex_network(self):
        # More complex network with multiple paths
        node_capacities = [20, 15, 30, 25, 10, 40, 35]
        connections = [
            (0, 1, 2), (0, 2, 4), (1, 3, 3), (1, 4, 8),
            (2, 4, 5), (2, 5, 7), (3, 6, 6), (4, 6, 4),
            (5, 6, 2)
        ]
        source = 0
        destination = 6
        data_size = 200
        latency_budget = 15
        
        result = find_optimal_path(7, node_capacities, connections, source, destination, data_size, latency_budget)
        # We don't assert the exact path since multiple valid paths may exist,
        # but we check that it's a valid path from source to destination
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[-1], 6)
    
    def test_high_processing_cost(self):
        # Path with lower latency but higher processing cost vs path with higher latency but lower processing cost
        node_capacities = [10, 5, 100, 50]
        connections = [(0, 1, 2), (0, 2, 10), (1, 3, 2), (2, 3, 5)]
        source = 0
        destination = 3
        data_size = 200
        latency_budget = 20
        
        # Path [0,1,3] has latency 4 but high processing cost due to node 1's low capacity
        # Path [0,2,3] has latency 15 but lower processing cost due to node 2's high capacity
        result = find_optimal_path(4, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[-1], 3)
    
    def test_edge_case_large_data(self):
        # Test with large data size
        node_capacities = [100, 200, 150]
        connections = [(0, 1, 5), (1, 2, 5)]
        source = 0
        destination = 2
        data_size = 10000
        latency_budget = 100
        
        expected = [0, 1, 2]
        result = find_optimal_path(3, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(result, expected)
    
    def test_edge_case_zero_latency_budget(self):
        # Test with zero latency budget
        node_capacities = [10, 20]
        connections = [(0, 1, 5)]
        source = 0
        destination = 1
        data_size = 100
        latency_budget = 0
        
        expected = []  # No valid path within budget
        result = find_optimal_path(2, node_capacities, connections, source, destination, data_size, latency_budget)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()