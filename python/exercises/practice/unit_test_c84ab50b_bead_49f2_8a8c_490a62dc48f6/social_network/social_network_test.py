import unittest
from social_network import SocialNetwork

class TestSocialNetwork(unittest.TestCase):
    def setUp(self):
        self.network = SocialNetwork()

    def test_add_user(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(1)  # Duplicate
        self.assertEqual(len(self.network.get_all_users()), 2)

    def test_remove_user(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.connect(1, 2, 5)
        self.network.remove_user(1)
        self.assertEqual(len(self.network.get_all_users()), 1)
        self.assertEqual(self.network.get_shortest_path(1, 2), -1)

    def test_connect_disconnect(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.connect(1, 2, 5)
        self.assertEqual(self.network.get_shortest_path(1, 2), 5)
        self.network.disconnect(1, 2)
        self.assertEqual(self.network.get_shortest_path(1, 2), -1)

    def test_latency_update(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.connect(1, 2, 5)
        self.network.connect(1, 2, 10)  # Update latency
        self.assertEqual(self.network.get_shortest_path(1, 2), 10)

    def test_shortest_path_complex(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(3)
        self.network.add_user(4)
        self.network.connect(1, 2, 1)
        self.network.connect(2, 3, 2)
        self.network.connect(3, 4, 3)
        self.network.connect(1, 4, 10)
        self.assertEqual(self.network.get_shortest_path(1, 4), 6)

    def test_nonexistent_users(self):
        self.assertEqual(self.network.get_shortest_path(1, 2), -1)
        self.assertEqual(self.network.get_kth_neighbor(1, 1), -1)
        self.network.connect(1, 2, 5)  # No users exist
        self.network.disconnect(1, 2)  # No users exist

    def test_get_kth_neighbor(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(3)
        self.network.connect(1, 2, 1)
        self.network.connect(1, 3, 1)
        self.assertEqual(self.network.get_kth_neighbor(1, 1), 2)
        self.assertEqual(self.network.get_kth_neighbor(1, 2), 3)
        self.assertEqual(self.network.get_kth_neighbor(1, 3), -1)

    def test_get_kth_neighbor_invalid_k(self):
        self.network.add_user(1)
        with self.assertRaises(ValueError):
            self.network.get_kth_neighbor(1, 0)
        with self.assertRaises(ValueError):
            self.network.get_kth_neighbor(1, -1)

    def test_network_partition(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(3)
        self.network.add_user(4)
        self.network.connect(1, 2, 1)
        self.network.connect(3, 4, 1)
        self.assertEqual(self.network.get_shortest_path(1, 3), -1)
        self.assertEqual(self.network.get_shortest_path(2, 4), -1)

    def test_remove_connection_affects_paths(self):
        self.network.add_user(1)
        self.network.add_user(2)
        self.network.add_user(3)
        self.network.connect(1, 2, 1)
        self.network.connect(2, 3, 1)
        self.network.disconnect(2, 3)
        self.assertEqual(self.network.get_shortest_path(1, 3), -1)

if __name__ == '__main__':
    unittest.main()