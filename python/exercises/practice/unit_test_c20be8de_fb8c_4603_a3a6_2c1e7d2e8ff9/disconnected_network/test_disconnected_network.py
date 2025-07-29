import unittest
from disconnected_network import SocialNetwork

class TestSocialNetwork(unittest.TestCase):
    def setUp(self):
        self.network = SocialNetwork()

    def test_empty_network(self):
        self.assertEqual(self.network.get_largest_community_size(), 0)
        self.assertEqual(self.network.get_community_count(), 0)
        self.assertFalse(self.network.are_users_connected(1, 2))

    def test_single_user(self):
        self.network.add_user(1)
        self.assertEqual(self.network.get_largest_community_size(), 1)
        self.assertEqual(self.network.get_community_count(), 1)

    def test_duplicate_user(self):
        self.network.add_user(1)
        self.network.add_user(1)
        self.assertEqual(self.network.get_largest_community_size(), 1)
        self.assertEqual(self.network.get_community_count(), 1)

    def test_remove_nonexistent_user(self):
        self.network.remove_user(1)
        self.assertEqual(self.network.get_largest_community_size(), 0)
        self.assertEqual(self.network.get_community_count(), 0)

    def test_simple_connection(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_connection(1, 2)
        self.assertTrue(self.network.are_users_connected(1, 2))
        self.assertEqual(self.network.get_largest_community_size(), 2)
        self.assertEqual(self.network.get_community_count(), 1)

    def test_self_connection(self):
        self.network.add_user(1)
        self.network.add_connection(1, 1)
        self.assertEqual(self.network.get_largest_community_size(), 1)
        self.assertEqual(self.network.get_community_count(), 1)

    def test_multiple_communities(self):
        # Community 1: 1-2-3
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(3)
        self.network.add_connection(1, 2)
        self.network.add_connection(2, 3)
        
        # Community 2: 4-5
        self.network.add_user(4)
        self.network.add_user(5)
        self.network.add_connection(4, 5)

        self.assertEqual(self.network.get_largest_community_size(), 3)
        self.assertEqual(self.network.get_community_count(), 2)
        self.assertTrue(self.network.are_users_connected(1, 3))
        self.assertFalse(self.network.are_users_connected(1, 4))

    def test_remove_bridge_connection(self):
        # Create a path: 1-2-3
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(3)
        self.network.add_connection(1, 2)
        self.network.add_connection(2, 3)
        
        # Remove bridge
        self.network.remove_connection(2, 3)
        
        self.assertFalse(self.network.are_users_connected(1, 3))
        self.assertEqual(self.network.get_community_count(), 2)

    def test_remove_user_with_connections(self):
        # Create a star formation: 1 connected to 2,3,4
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(3)
        self.network.add_user(4)
        self.network.add_connection(1, 2)
        self.network.add_connection(1, 3)
        self.network.add_connection(1, 4)
        
        # Remove central node
        self.network.remove_user(1)
        
        self.assertEqual(self.network.get_largest_community_size(), 1)
        self.assertEqual(self.network.get_community_count(), 3)
        self.assertFalse(self.network.are_users_connected(2, 3))

    def test_large_network(self):
        # Create a chain of 1000 users
        for i in range(1, 1001):
            self.network.add_user(i)
            if i > 1:
                self.network.add_connection(i-1, i)
        
        self.assertEqual(self.network.get_largest_community_size(), 1000)
        self.assertEqual(self.network.get_community_count(), 1)
        self.assertTrue(self.network.are_users_connected(1, 1000))

    def test_complex_operations(self):
        # Add users and connections
        for i in range(1, 6):
            self.network.add_user(i)
        
        # Create two communities: (1-2-3) and (4-5)
        self.network.add_connection(1, 2)
        self.network.add_connection(2, 3)
        self.network.add_connection(4, 5)
        
        self.assertEqual(self.network.get_largest_community_size(), 3)
        self.assertEqual(self.network.get_community_count(), 2)
        
        # Join communities
        self.network.add_connection(3, 4)
        self.assertEqual(self.network.get_largest_community_size(), 5)
        self.assertEqual(self.network.get_community_count(), 1)
        
        # Split communities
        self.network.remove_connection(3, 4)
        self.assertEqual(self.network.get_largest_community_size(), 3)
        self.assertEqual(self.network.get_community_count(), 2)

    def test_edge_cases(self):
        # Test invalid connections
        self.network.add_connection(1, 2)  # Neither user exists
        self.assertEqual(self.network.get_community_count(), 0)
        
        self.network.add_user(1)
        self.network.add_connection(1, 2)  # One user doesn't exist
        self.assertEqual(self.network.get_largest_community_size(), 1)
        
        # Test removing non-existent connections
        self.network.remove_connection(1, 2)
        self.assertEqual(self.network.get_largest_community_size(), 1)
        
        # Test with very large user IDs
        large_id1 = 1000000000
        large_id2 = 999999999
        self.network.add_user(large_id1)
        self.network.add_user(large_id2)
        self.network.add_connection(large_id1, large_id2)
        self.assertTrue(self.network.are_users_connected(large_id1, large_id2))

if __name__ == '__main__':
    unittest.main()