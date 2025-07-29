import unittest
from trade_optimizer import GalacticTradeNetwork


class GalacticTradeNetworkTest(unittest.TestCase):
    def setUp(self):
        # Initialize a fresh trade network for each test
        self.trade_network = GalacticTradeNetwork()

    def test_empty_network(self):
        # Test with an empty network
        self.assertEqual(self.trade_network.max_flow(1, 2, 10), 0)

    def test_single_path(self):
        # Create a simple network with one path
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_star_system(3, 0)
        self.trade_network.add_trade_route(1, 2, 5, 2)  # Capacity 5, Time 2
        self.trade_network.add_trade_route(2, 3, 3, 3)  # Capacity 3, Time 3
        
        # Test max flow from 1 to 3 with different time limits
        self.assertEqual(self.trade_network.max_flow(1, 3, 4), 0)  # Not enough time
        self.assertEqual(self.trade_network.max_flow(1, 3, 5), 3)  # Just enough time
        self.assertEqual(self.trade_network.max_flow(1, 3, 10), 3)  # More than enough time

    def test_multiple_paths(self):
        # Create a network with multiple paths
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_star_system(3, 0)
        self.trade_network.add_star_system(4, 0)
        
        # Path 1: 1->2->4 (Capacity 5, Time 5)
        self.trade_network.add_trade_route(1, 2, 10, 2)
        self.trade_network.add_trade_route(2, 4, 5, 3)
        
        # Path 2: 1->3->4 (Capacity 7, Time 6)
        self.trade_network.add_trade_route(1, 3, 10, 3)
        self.trade_network.add_trade_route(3, 4, 7, 3)
        
        # Test max flow with different time limits
        self.assertEqual(self.trade_network.max_flow(1, 4, 4), 0)  # Not enough time for any path
        self.assertEqual(self.trade_network.max_flow(1, 4, 5), 5)  # Only path 1 is usable
        self.assertEqual(self.trade_network.max_flow(1, 4, 6), 12)  # Both paths are usable

    def test_update_trade_route(self):
        # Set up a basic network
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_trade_route(1, 2, 5, 3)
        
        # Test initial max flow
        self.assertEqual(self.trade_network.max_flow(1, 2, 3), 5)
        
        # Update capacity and test again
        self.trade_network.update_trade_route_capacity(1, 2, 8)
        self.assertEqual(self.trade_network.max_flow(1, 2, 3), 8)
        
        # Update travel time and test again
        self.trade_network.update_trade_route_travel_time(1, 2, 4)
        self.assertEqual(self.trade_network.max_flow(1, 2, 3), 0)  # Not enough time
        self.assertEqual(self.trade_network.max_flow(1, 2, 4), 8)  # Just enough time

    def test_remove_trade_route(self):
        # Set up a network with multiple paths
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_star_system(3, 0)
        self.trade_network.add_trade_route(1, 2, 5, 2)
        self.trade_network.add_trade_route(2, 3, 5, 2)
        self.trade_network.add_trade_route(1, 3, 3, 5)
        
        # Test initial max flow
        self.assertEqual(self.trade_network.max_flow(1, 3, 4), 5)  # Path through 2
        
        # Remove a trade route and test again
        self.trade_network.remove_trade_route(1, 2)
        self.assertEqual(self.trade_network.max_flow(1, 3, 4), 0)  # Not enough time for direct path
        self.assertEqual(self.trade_network.max_flow(1, 3, 5), 3)  # Direct path is now usable

    def test_remove_star_system(self):
        # Set up a network with multiple star systems
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_star_system(3, 0)
        self.trade_network.add_star_system(4, 0)
        self.trade_network.add_trade_route(1, 2, 5, 2)
        self.trade_network.add_trade_route(2, 3, 5, 2)
        self.trade_network.add_trade_route(3, 4, 5, 2)
        
        # Test initial max flow
        self.assertEqual(self.trade_network.max_flow(1, 4, 6), 5)
        
        # Remove a star system and test again
        self.trade_network.remove_star_system(3)
        self.assertEqual(self.trade_network.max_flow(1, 4, 6), 0)  # No path exists

    def test_demand_updates(self):
        # Test that demand values are stored and updated correctly
        self.trade_network.add_star_system(1, 5)
        self.assertEqual(self.trade_network.get_demand(1), 5)
        
        # Update demand and test again
        self.trade_network.update_demand(1, 10)
        self.assertEqual(self.trade_network.get_demand(1), 10)

    def test_same_source_destination(self):
        # Test when source and destination are the same
        self.trade_network.add_star_system(1, 0)
        self.assertEqual(self.trade_network.max_flow(1, 1, 5), 0)

    def test_disconnected_network(self):
        # Test with disconnected components
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_star_system(3, 0)
        self.trade_network.add_star_system(4, 0)
        
        # Connect 1->2 and 3->4 but not 2->3
        self.trade_network.add_trade_route(1, 2, 5, 2)
        self.trade_network.add_trade_route(3, 4, 5, 2)
        
        # Test flow between disconnected components
        self.assertEqual(self.trade_network.max_flow(1, 4, 10), 0)

    def test_zero_capacity_route(self):
        # Test with a zero-capacity trade route
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_trade_route(1, 2, 0, 2)
        
        # Test flow with zero capacity
        self.assertEqual(self.trade_network.max_flow(1, 2, 10), 0)

    def test_invalid_inputs(self):
        # Test handling of invalid inputs
        with self.assertRaises(ValueError):
            self.trade_network.add_trade_route(1, 2, 5, -1)  # Negative travel time
            
        with self.assertRaises(ValueError):
            self.trade_network.add_trade_route(1, 2, -5, 2)  # Negative capacity
            
        with self.assertRaises(ValueError):
            self.trade_network.max_flow(1, 2, -5)  # Negative time limit

    def test_complex_network(self):
        # Test with a more complex network
        self.trade_network.add_star_system(1, 0)
        self.trade_network.add_star_system(2, 0)
        self.trade_network.add_star_system(3, 0)
        self.trade_network.add_star_system(4, 0)
        self.trade_network.add_star_system(5, 0)
        self.trade_network.add_star_system(6, 0)
        
        # Create multiple paths with different capacities and times
        self.trade_network.add_trade_route(1, 2, 16, 2)
        self.trade_network.add_trade_route(1, 3, 13, 3)
        self.trade_network.add_trade_route(2, 3, 10, 1)
        self.trade_network.add_trade_route(2, 4, 12, 4)
        self.trade_network.add_trade_route(3, 2, 4, 1)
        self.trade_network.add_trade_route(3, 5, 14, 2)
        self.trade_network.add_trade_route(4, 3, 9, 1)
        self.trade_network.add_trade_route(4, 6, 20, 3)
        self.trade_network.add_trade_route(5, 4, 7, 2)
        self.trade_network.add_trade_route(5, 6, 4, 1)
        
        # Test max flow with different time limits
        self.assertEqual(self.trade_network.max_flow(1, 6, 5), 0)
        self.assertEqual(self.trade_network.max_flow(1, 6, 6), 4)  # Path: 1->3->5->6
        self.assertEqual(self.trade_network.max_flow(1, 6, 9), 16)  # Path: 1->3->5->6 and 1->2->4->6


if __name__ == '__main__':
    unittest.main()