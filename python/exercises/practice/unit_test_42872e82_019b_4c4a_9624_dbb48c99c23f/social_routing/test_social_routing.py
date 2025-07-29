import unittest
from social_routing import SocialNetwork

class TestSocialNetwork(unittest.TestCase):
    def setUp(self):
        self.network = SocialNetwork()

    def test_basic_routing(self):
        # Create a simple network
        self.network.addUser(1)
        self.network.addUser(2)
        self.network.addUser(3)
        self.network.addFriendship(1, 2)
        self.network.addFriendship(2, 3)

        # Test direct connection
        self.assertEqual(self.network.getRoute(1, 2, 1), 1)
        # Test two-hop connection
        self.assertEqual(self.network.getRoute(1, 3, 2), 2)
        # Test unreachable within limit
        self.assertEqual(self.network.getRoute(1, 3, 1), -1)

    def test_complex_routing(self):
        # Create a more complex network
        for i in range(1, 7):
            self.network.addUser(i)
        
        # Create a circular network with some shortcuts
        self.network.addFriendship(1, 2)
        self.network.addFriendship(2, 3)
        self.network.addFriendship(3, 4)
        self.network.addFriendship(4, 5)
        self.network.addFriendship(5, 6)
        self.network.addFriendship(6, 1)
        self.network.addFriendship(1, 4)  # shortcut

        # Test various paths
        self.assertEqual(self.network.getRoute(1, 4, 1), 1)  # Direct shortcut
        self.assertEqual(self.network.getRoute(1, 3, 2), 2)  # Through node 2
        self.assertEqual(self.network.getRoute(1, 5, 2), 2)  # Through shortcut
        self.assertEqual(self.network.getRoute(2, 6, 2), 2)  # Through node 3->4

    def test_user_removal(self):
        # Setup network
        for i in range(1, 5):
            self.network.addUser(i)
        self.network.addFriendship(1, 2)
        self.network.addFriendship(2, 3)
        self.network.addFriendship(3, 4)

        # Test before removal
        self.assertEqual(self.network.getRoute(1, 4, 3), 3)

        # Remove middle node
        self.network.removeUser(2)

        # Test after removal
        self.assertEqual(self.network.getRoute(1, 4, 3), -1)

    def test_friendship_changes(self):
        # Setup network
        for i in range(1, 4):
            self.network.addUser(i)
        self.network.addFriendship(1, 2)
        self.network.addFriendship(2, 3)

        # Test initial path
        self.assertEqual(self.network.getRoute(1, 3, 2), 2)

        # Remove friendship and test
        self.network.removeFriendship(2, 3)
        self.assertEqual(self.network.getRoute(1, 3, 2), -1)

        # Add direct friendship and test
        self.network.addFriendship(1, 3)
        self.assertEqual(self.network.getRoute(1, 3, 1), 1)

    def test_invalid_operations(self):
        # Test operations with non-existent users
        self.network.addUser(1)
        self.network.addUser(2)
        
        # Invalid friendship
        self.network.addFriendship(1, 3)  # Should not raise error but not create friendship
        self.assertEqual(self.network.getRoute(1, 3, 1), -1)

        # Invalid user removal
        self.network.removeUser(3)  # Should not raise error
        
        # Invalid friendship removal
        self.network.removeFriendship(1, 3)  # Should not raise error

    def test_large_k_values(self):
        # Create a chain of users
        for i in range(1, 11):
            self.network.addUser(i)
            if i > 1:
                self.network.addFriendship(i-1, i)

        # Test with different K values
        self.assertEqual(self.network.getRoute(1, 5, 4), 4)
        self.assertEqual(self.network.getRoute(1, 5, 3), -1)
        self.assertEqual(self.network.getRoute(1, 10, 9), 9)
        self.assertEqual(self.network.getRoute(1, 10, 8), -1)

    def test_multiple_paths(self):
        # Create a network with multiple possible paths
        for i in range(1, 5):
            self.network.addUser(i)
        
        # Create a diamond shape
        self.network.addFriendship(1, 2)
        self.network.addFriendship(1, 3)
        self.network.addFriendship(2, 4)
        self.network.addFriendship(3, 4)

        # Should return the shortest path
        self.assertEqual(self.network.getRoute(1, 4, 2), 2)

    def test_edge_cases(self):
        # Test same user route
        self.network.addUser(1)
        self.assertEqual(self.network.getRoute(1, 1, 1), 0)

        # Test with K = 0
        self.network.addUser(2)
        self.network.addFriendship(1, 2)
        self.assertEqual(self.network.getRoute(1, 2, 0), -1)

        # Test with very large K
        self.assertEqual(self.network.getRoute(1, 2, 100), 1)

if __name__ == '__main__':
    unittest.main()