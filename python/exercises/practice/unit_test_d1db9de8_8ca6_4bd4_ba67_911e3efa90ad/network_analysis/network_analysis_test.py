import unittest
from network_analysis import SocialNetwork


class NetworkAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.network_small = SocialNetwork(5)
        self.network_medium = SocialNetwork(10)
        self.network_large = SocialNetwork(100)

    def test_connect_and_are_connected_basic(self):
        self.network_small.connect(0, 1)
        self.assertTrue(self.network_small.are_connected(0, 1))
        self.assertTrue(self.network_small.are_connected(1, 0))
        self.assertFalse(self.network_small.are_connected(0, 2))

    def test_self_connection(self):
        # User connecting to themselves should be connected
        self.network_small.connect(0, 0)
        self.assertTrue(self.network_small.are_connected(0, 0))

    def test_transitive_connections(self):
        self.network_small.connect(0, 1)
        self.network_small.connect(1, 2)
        self.assertTrue(self.network_small.are_connected(0, 2))
        self.assertFalse(self.network_small.are_connected(0, 3))

    def test_multiple_components(self):
        # Create two separate components
        self.network_small.connect(0, 1)
        self.network_small.connect(2, 3)
        
        self.assertTrue(self.network_small.are_connected(0, 1))
        self.assertTrue(self.network_small.are_connected(2, 3))
        self.assertFalse(self.network_small.are_connected(0, 2))
        self.assertFalse(self.network_small.are_connected(1, 3))

    def test_largest_component_size_basic(self):
        # Empty network
        self.assertEqual(self.network_small.largest_component_size(), 1)
        
        # One connection
        self.network_small.connect(0, 1)
        self.assertEqual(self.network_small.largest_component_size(), 2)
        
        # Two separate components of size 2
        self.network_small.connect(2, 3)
        self.assertEqual(self.network_small.largest_component_size(), 2)
        
        # Connect the components
        self.network_small.connect(1, 2)
        self.assertEqual(self.network_small.largest_component_size(), 4)

    def test_largest_component_size_complex(self):
        # Create a larger component
        for i in range(8):
            self.network_medium.connect(i, (i + 1) % 9)
        
        # Create a smaller component
        self.network_medium.connect(9, 9)
        
        self.assertEqual(self.network_medium.largest_component_size(), 9)

    def test_min_connections_to_separate_basic(self):
        # Not connected users
        self.assertEqual(self.network_small.min_connections_to_separate(0, 1), 0)
        
        # Direct connection
        self.network_small.connect(0, 1)
        self.assertEqual(self.network_small.min_connections_to_separate(0, 1), 1)
        
        # Multiple paths
        self.network_small.connect(0, 2)
        self.network_small.connect(1, 2)
        self.assertEqual(self.network_small.min_connections_to_separate(0, 1), 2)

    def test_min_connections_to_separate_complex(self):
        # Create a square with diagonal
        self.network_small.connect(0, 1)
        self.network_small.connect(1, 2)
        self.network_small.connect(2, 3)
        self.network_small.connect(3, 0)
        self.network_small.connect(0, 2)  # diagonal
        
        # It takes 3 connections to separate 0 and 2
        self.assertEqual(self.network_small.min_connections_to_separate(0, 2), 3)
        # It takes 2 connections to separate 0 and 3
        self.assertEqual(self.network_small.min_connections_to_separate(0, 3), 2)

    def test_large_network_performance(self):
        # Create a large network with a line topology
        for i in range(99):
            self.network_large.connect(i, i + 1)
        
        # Test basic operations
        self.assertTrue(self.network_large.are_connected(0, 99))
        self.assertEqual(self.network_large.largest_component_size(), 100)
        
        # Test min_connections_to_separate with a single path
        self.assertEqual(self.network_large.min_connections_to_separate(0, 99), 1)

    def test_cyclic_connections(self):
        # Create a cycle: 0-1-2-3-0
        self.network_small.connect(0, 1)
        self.network_small.connect(1, 2)
        self.network_small.connect(2, 3)
        self.network_small.connect(3, 0)
        
        self.assertTrue(self.network_small.are_connected(0, 2))
        self.assertEqual(self.network_small.largest_component_size(), 4)
        self.assertEqual(self.network_small.min_connections_to_separate(0, 2), 2)

    def test_reconnect_existing_connection(self):
        self.network_small.connect(0, 1)
        self.network_small.connect(0, 1)  # Connect again
        
        # Should still be connected
        self.assertTrue(self.network_small.are_connected(0, 1))
        # Component size should not change
        self.assertEqual(self.network_small.largest_component_size(), 2)

    def test_isolated_user(self):
        # Connect users 0-1-2-3
        self.network_small.connect(0, 1)
        self.network_small.connect(1, 2)
        self.network_small.connect(2, 3)
        
        # User 4 is isolated
        self.assertFalse(self.network_small.are_connected(0, 4))
        self.assertEqual(self.network_small.min_connections_to_separate(0, 4), 0)
        
        # Connect user 4
        self.network_small.connect(3, 4)
        self.assertTrue(self.network_small.are_connected(0, 4))
        self.assertEqual(self.network_small.largest_component_size(), 5)


if __name__ == "__main__":
    unittest.main()