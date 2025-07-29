import unittest
from server_placement import optimize_server_placement

class ServerPlacementTest(unittest.TestCase):
    def test_simple_network(self):
        nodes = [1, 2, 3, 4]
        edges = [(1, 2, 10), (2, 3, 5), (3, 4, 10), (1, 4, 2)]
        client_requests = [(1, 3, 7), (4, 3, 3)]
        initial_server_locations = [3]
        max_server_count = 2
        
        result = optimize_server_placement(nodes, edges, client_requests, 
                                        initial_server_locations, max_server_count)
        
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(x, int) for x in result))
        self.assertTrue(len(result) <= max_server_count)
        self.assertTrue(all(x in nodes for x in result))
        self.assertTrue(all(x in result for x in initial_server_locations))

    def test_disconnected_network(self):
        nodes = [1, 2, 3, 4, 5]
        edges = [(1, 2, 10), (4, 5, 10)]  # Two disconnected components
        client_requests = [(1, 4, 5)]
        initial_server_locations = [4]
        max_server_count = 2
        
        with self.assertRaises(ValueError):
            optimize_server_placement(nodes, edges, client_requests, 
                                   initial_server_locations, max_server_count)

    def test_empty_network(self):
        nodes = []
        edges = []
        client_requests = []
        initial_server_locations = []
        max_server_count = 0
        
        result = optimize_server_placement(nodes, edges, client_requests, 
                                        initial_server_locations, max_server_count)
        self.assertEqual(result, [])

    def test_single_node(self):
        nodes = [1]
        edges = []
        client_requests = []
        initial_server_locations = [1]
        max_server_count = 1
        
        result = optimize_server_placement(nodes, edges, client_requests, 
                                        initial_server_locations, max_server_count)
        self.assertEqual(result, [1])

    def test_zero_capacity_edge(self):
        nodes = [1, 2, 3]
        edges = [(1, 2, 0), (2, 3, 5)]
        client_requests = [(1, 3, 1)]
        initial_server_locations = [3]
        max_server_count = 2
        
        with self.assertRaises(ValueError):
            optimize_server_placement(nodes, edges, client_requests, 
                                   initial_server_locations, max_server_count)

    def test_large_network(self):
        # Create a larger network to test efficiency
        nodes = list(range(1, 101))  # 100 nodes
        edges = [(i, i+1, 10) for i in range(1, 100)]  # Linear network
        client_requests = [(1, 100, 5), (50, 100, 3)]
        initial_server_locations = [100]
        max_server_count = 3
        
        result = optimize_server_placement(nodes, edges, client_requests, 
                                        initial_server_locations, max_server_count)
        
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) <= max_server_count)

    def test_invalid_inputs(self):
        # Test with invalid node IDs in edges
        with self.assertRaises(ValueError):
            optimize_server_placement(
                nodes=[1, 2],
                edges=[(1, 3, 10)],  # Node 3 doesn't exist
                client_requests=[(1, 2, 1)],
                initial_server_locations=[2],
                max_server_count=1
            )

        # Test with invalid server locations
        with self.assertRaises(ValueError):
            optimize_server_placement(
                nodes=[1, 2],
                edges=[(1, 2, 10)],
                client_requests=[(1, 2, 1)],
                initial_server_locations=[3],  # Server 3 doesn't exist
                max_server_count=1
            )

        # Test with max_server_count less than initial servers
        with self.assertRaises(ValueError):
            optimize_server_placement(
                nodes=[1, 2, 3],
                edges=[(1, 2, 10), (2, 3, 10)],
                client_requests=[(1, 2, 1)],
                initial_server_locations=[2, 3],
                max_server_count=1  # Less than initial servers
            )

    def test_multiple_optimal_solutions(self):
        # Test case where multiple solutions have same congestion
        nodes = [1, 2, 3, 4]
        edges = [(1, 2, 10), (2, 3, 10), (3, 4, 10), (1, 4, 10)]
        client_requests = [(1, 3, 5), (4, 3, 5)]
        initial_server_locations = [3]
        max_server_count = 2
        
        result = optimize_server_placement(nodes, edges, client_requests, 
                                        initial_server_locations, max_server_count)
        
        self.assertIsInstance(result, list)
        self.assertTrue(3 in result)  # Initial server must be in result
        self.assertTrue(len(result) <= max_server_count)

    def test_zero_data_size_requests(self):
        nodes = [1, 2, 3]
        edges = [(1, 2, 5), (2, 3, 5)]
        client_requests = [(1, 3, 0)]  # Zero data size
        initial_server_locations = [3]
        max_server_count = 1
        
        result = optimize_server_placement(nodes, edges, client_requests, 
                                        initial_server_locations, max_server_count)
        
        self.assertEqual(result, [3])

if __name__ == '__main__':
    unittest.main()