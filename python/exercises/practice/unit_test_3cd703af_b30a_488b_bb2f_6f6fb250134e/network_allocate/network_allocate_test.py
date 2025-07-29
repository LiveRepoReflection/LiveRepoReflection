import unittest
from network_allocate import find_optimal_path

class NetworkAllocateTest(unittest.TestCase):
    def test_direct_path(self):
        # Simple case with direct path
        capacities = {(0, 1): 10.0}
        costs = {(0, 1): 2.0}
        allocations = {(0, 1): 3.0}
        source = 0
        destination = 1
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertEqual(result, ([0, 1], 10.0))  # 5.0 * 2.0 = 10.0
    
    def test_multiple_paths_choose_cheapest(self):
        capacities = {(0, 1): 10.0, (1, 2): 10.0, (0, 2): 5.0}
        costs = {(0, 1): 1.0, (1, 2): 1.0, (0, 2): 3.0}
        allocations = {(0, 1): 3.0, (1, 2): 2.0, (0, 2): 0.0}
        source = 0
        destination = 2
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertEqual(result, ([0, 1, 2], 10.0))  # 5.0 * (1.0 + 1.0) = 10.0 is cheaper than direct path at 15.0
    
    def test_insufficient_capacity(self):
        capacities = {(0, 1): 10.0, (1, 2): 3.0}
        costs = {(0, 1): 1.0, (1, 2): 1.0}
        allocations = {(0, 1): 3.0, (1, 2): 1.0}
        source = 0
        destination = 2
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertIsNone(result)  # Not enough capacity on path (1,2)
    
    def test_disconnected_graph(self):
        capacities = {(0, 1): 10.0, (2, 3): 10.0}
        costs = {(0, 1): 1.0, (2, 3): 1.0}
        allocations = {(0, 1): 0.0, (2, 3): 0.0}
        source = 0
        destination = 3
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertIsNone(result)  # No path from 0 to 3
    
    def test_complex_network(self):
        capacities = {
            (0, 1): 10.0, (0, 2): 5.0, (1, 2): 15.0, 
            (1, 3): 10.0, (2, 3): 10.0, (2, 4): 10.0, 
            (3, 4): 5.0, (3, 5): 15.0, (4, 5): 10.0
        }
        costs = {
            (0, 1): 1.0, (0, 2): 2.0, (1, 2): 1.0, 
            (1, 3): 3.0, (2, 3): 2.0, (2, 4): 3.0, 
            (3, 4): 1.0, (3, 5): 2.0, (4, 5): 1.0
        }
        allocations = {
            (0, 1): 5.0, (0, 2): 0.0, (1, 2): 5.0, 
            (1, 3): 5.0, (2, 3): 5.0, (2, 4): 5.0, 
            (3, 4): 0.0, (3, 5): 10.0, (4, 5): 5.0
        }
        source = 0
        destination = 5
        bandwidth = 3.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        # Expected optimal path is 0-2-4-5 with cost 6.0 (2.0 + 3.0 + 1.0) * 3.0 = 18.0
        self.assertEqual(result[1], 18.0)
        self.assertEqual(result[0][0], 0)
        self.assertEqual(result[0][-1], 5)
    
    def test_exactly_enough_capacity(self):
        capacities = {(0, 1): 10.0, (1, 2): 5.0}
        costs = {(0, 1): 1.0, (1, 2): 1.0}
        allocations = {(0, 1): 3.0, (1, 2): 0.0}
        source = 0
        destination = 2
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertEqual(result, ([0, 1, 2], 10.0))  # Exactly enough capacity on path (1,2)
    
    def test_floating_point_precision(self):
        capacities = {(0, 1): 10.0, (1, 2): 5.0}
        costs = {(0, 1): 1.0, (1, 2): 1.0}
        allocations = {(0, 1): 3.0, (1, 2): 0.0}
        source = 0
        destination = 2
        bandwidth = 4.999999
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertIsNotNone(result)  # Should handle floating point comparison correctly
        
    def test_empty_graph(self):
        capacities = {}
        costs = {}
        allocations = {}
        source = 0
        destination = 1
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertIsNone(result)  # No path in empty graph
    
    def test_self_loop(self):
        capacities = {(0, 0): 10.0}
        costs = {(0, 0): 1.0}
        allocations = {(0, 0): 0.0}
        source = 0
        destination = 0
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertEqual(result, ([0], 0.0))  # Source equals destination, no cost
    
    def test_large_values(self):
        # Test with very large values
        capacities = {(0, 1): 1e9, (1, 2): 1e9}
        costs = {(0, 1): 1e6, (1, 2): 1e6}
        allocations = {(0, 1): 0.0, (1, 2): 0.0}
        source = 0
        destination = 2
        bandwidth = 1e6
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertEqual(result, ([0, 1, 2], 2e12))  # 1e6 * (1e6 + 1e6) = 2e12
    
    def test_invalid_inputs(self):
        # Test with invalid router indices
        capacities = {(0, 1): 10.0}
        costs = {(0, 1): 1.0}
        allocations = {(0, 1): 0.0}
        source = 0
        destination = 2  # Router 2 doesn't exist
        bandwidth = 5.0
        
        result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
        self.assertIsNone(result)  # No path to non-existent router

if __name__ == '__main__':
    unittest.main()