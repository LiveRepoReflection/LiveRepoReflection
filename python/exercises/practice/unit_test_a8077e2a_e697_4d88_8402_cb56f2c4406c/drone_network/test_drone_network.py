import unittest
from drone_network import optimal_drone_network

class TestDroneNetwork(unittest.TestCase):
    def test_basic_case(self):
        grid_size = 4
        location_data = [
            (0, 0, 10, 5),  # x, y, hub_cost, demand
            (0, 1, 12, 3),
            (1, 0, 15, 2),
            (1, 1, 8, 7),
            (2, 2, 11, 4),
            (2, 3, 9, 6),
            (3, 2, 13, 1),
            (3, 3, 7, 8)
        ]
        max_hubs = 2
        
        hub_locations, total_cost = optimal_drone_network(grid_size, location_data, max_hubs)
        
        # Check the output format
        self.assertIsInstance(hub_locations, list)
        self.assertEqual(len(hub_locations), max_hubs)
        for loc in hub_locations:
            self.assertIsInstance(loc, tuple)
            self.assertEqual(len(loc), 2)
            self.assertGreaterEqual(loc[0], 0)
            self.assertLess(loc[0], grid_size)
            self.assertGreaterEqual(loc[1], 0)
            self.assertLess(loc[1], grid_size)
        
        self.assertIsInstance(total_cost, int)
        
        # Ensure all hub locations are from the location_data
        valid_coords = [(x, y) for x, y, _, _ in location_data]
        for loc in hub_locations:
            self.assertIn(loc, valid_coords)
    
    def test_single_hub(self):
        grid_size = 3
        location_data = [
            (0, 0, 5, 2),
            (1, 1, 10, 3),
            (2, 2, 15, 4)
        ]
        max_hubs = 1
        
        hub_locations, total_cost = optimal_drone_network(grid_size, location_data, max_hubs)
        self.assertEqual(len(hub_locations), 1)

    def test_zero_demand(self):
        grid_size = 2
        location_data = [
            (0, 0, 10, 0),
            (0, 1, 12, 0),
            (1, 0, 15, 0),
            (1, 1, 8, 0)
        ]
        max_hubs = 2
        
        hub_locations, total_cost = optimal_drone_network(grid_size, location_data, max_hubs)
        # Since all demands are zero, the optimal solution should only have hub establishment costs
        min_hub_cost_locations = sorted(location_data, key=lambda x: x[2])[:max_hubs]
        expected_cost = sum(loc[2] for loc in min_hub_cost_locations)
        self.assertEqual(total_cost, expected_cost)

    def test_high_hub_cost(self):
        grid_size = 3
        location_data = [
            (0, 0, 1000, 5),  # Very high hub cost
            (0, 1, 10, 2),
            (1, 0, 10, 3),
            (1, 1, 10, 4)
        ]
        max_hubs = 2
        
        hub_locations, total_cost = optimal_drone_network(grid_size, location_data, max_hubs)
        # The optimal solution should avoid the high-cost location
        self.assertNotIn((0, 0), hub_locations)

    def test_max_hubs_equals_locations(self):
        grid_size = 2
        location_data = [
            (0, 0, 10, 5),
            (1, 1, 8, 7)
        ]
        max_hubs = 2
        
        hub_locations, total_cost = optimal_drone_network(grid_size, location_data, max_hubs)
        # All locations should be hubs
        self.assertEqual(len(hub_locations), 2)
        self.assertIn((0, 0), hub_locations)
        self.assertIn((1, 1), hub_locations)
        # Total cost should equal sum of hub costs (no delivery costs)
        self.assertEqual(total_cost, 18)

    def test_large_grid(self):
        grid_size = 10
        location_data = [
            (x, y, 10 + x + y, 5) 
            for x in range(10) for y in range(10)
        ]
        max_hubs = 5
        
        hub_locations, total_cost = optimal_drone_network(grid_size, location_data, max_hubs)
        self.assertEqual(len(hub_locations), max_hubs)
        
    def test_identical_locations(self):
        grid_size = 3
        location_data = [
            (1, 1, 10, 5),
            (1, 1, 15, 3),  # Same location, different cost/demand
            (2, 2, 12, 4)
        ]
        max_hubs = 2
        
        with self.assertRaises(ValueError):
            optimal_drone_network(grid_size, location_data, max_hubs)

    def test_out_of_bounds_location(self):
        grid_size = 3
        location_data = [
            (1, 1, 10, 5),
            (3, 3, 15, 3),  # Out of bounds
            (2, 2, 12, 4)
        ]
        max_hubs = 2
        
        with self.assertRaises(ValueError):
            optimal_drone_network(grid_size, location_data, max_hubs)

    def test_negative_hub_cost(self):
        grid_size = 3
        location_data = [
            (1, 1, -10, 5),  # Negative hub cost
            (2, 2, 12, 4)
        ]
        max_hubs = 2
        
        with self.assertRaises(ValueError):
            optimal_drone_network(grid_size, location_data, max_hubs)

    def test_negative_demand(self):
        grid_size = 3
        location_data = [
            (1, 1, 10, -5),  # Negative demand
            (2, 2, 12, 4)
        ]
        max_hubs = 2
        
        with self.assertRaises(ValueError):
            optimal_drone_network(grid_size, location_data, max_hubs)

if __name__ == '__main__':
    unittest.main()