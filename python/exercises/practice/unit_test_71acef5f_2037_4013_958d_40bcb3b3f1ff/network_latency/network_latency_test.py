import unittest
from network_latency import optimize_network_latency
import math

class TestNetworkLatency(unittest.TestCase):

    def test_empty_users(self):
        users = []
        friendships = []
        potential_server_locations = [(37.7749, -122.4194), (40.7128, -74.0060)]
        num_servers = 1
        
        def mock_latency(coord1, coord2):
            return 100.0

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertEqual(result, 0.0)

    def test_no_friendships(self):
        users = [1, 2, 3]
        friendships = []
        potential_server_locations = [(37.7749, -122.4194), (40.7128, -74.0060)]
        num_servers = 1
        
        def mock_latency(coord1, coord2):
            return 100.0

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertEqual(result, 0.0)

    def test_no_servers(self):
        users = [1, 2, 3]
        friendships = [(1, 2), (2, 3)]
        potential_server_locations = [(37.7749, -122.4194), (40.7128, -74.0060)]
        num_servers = 0
        
        # Manhattan distance for simplicity
        def mock_latency(coord1, coord2):
            return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

        # With no servers, we expect the average latency between friends directly
        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        
        # User 1 has one friend (2)
        # User 2 has two friends (1, 3)
        # User 3 has one friend (2)
        # Without servers, the latency is the direct distance between friends
        # For simplicity, we assume users are at the server locations
        expected = 0.0  # This would be calculated based on our latency function and user locations
        self.assertGreaterEqual(result, 0.0)

    def test_simple_network(self):
        users = [1, 2, 3, 4]
        friendships = [(1, 2), (2, 3), (3, 4)]
        potential_server_locations = [(0.0, 0.0), (10.0, 10.0)]
        num_servers = 1
        
        # Simple distance function for testing
        def mock_latency(coord1, coord2):
            return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertGreaterEqual(result, 0.0)

    def test_multiple_servers(self):
        users = [1, 2, 3, 4, 5, 6]
        friendships = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)]
        potential_server_locations = [(0.0, 0.0), (10.0, 0.0), (0.0, 10.0), (10.0, 10.0)]
        num_servers = 2
        
        def mock_latency(coord1, coord2):
            return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertGreaterEqual(result, 0.0)

    def test_disconnected_graph(self):
        users = [1, 2, 3, 4, 5, 6]
        friendships = [(1, 2), (2, 3), (4, 5), (5, 6)]  # Two disconnected components
        potential_server_locations = [(0.0, 0.0), (10.0, 0.0), (0.0, 10.0)]
        num_servers = 2
        
        def mock_latency(coord1, coord2):
            return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertGreaterEqual(result, 0.0)

    def test_all_potential_locations_as_servers(self):
        users = [1, 2, 3, 4]
        friendships = [(1, 2), (2, 3), (3, 4), (4, 1)]
        potential_server_locations = [(0.0, 0.0), (10.0, 0.0)]
        num_servers = 2  # Use all available locations
        
        def mock_latency(coord1, coord2):
            return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertGreaterEqual(result, 0.0)

    def test_more_servers_than_locations(self):
        users = [1, 2, 3]
        friendships = [(1, 2), (2, 3)]
        potential_server_locations = [(0.0, 0.0), (10.0, 0.0)]
        num_servers = 3  # More servers than locations
        
        def mock_latency(coord1, coord2):
            return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertGreaterEqual(result, 0.0)

    def test_complex_network(self):
        users = list(range(1, 21))  # 20 users
        # Create a more complex friendship network
        friendships = [(i, i+1) for i in range(1, 20)] + [(1, 5), (5, 10), (10, 15), (15, 20)]
        
        # More potential server locations
        potential_server_locations = [
            (0.0, 0.0), (10.0, 0.0), (0.0, 10.0), (10.0, 10.0),
            (5.0, 5.0), (15.0, 5.0), (5.0, 15.0), (15.0, 15.0)
        ]
        num_servers = 3
        
        def mock_latency(coord1, coord2):
            return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        self.assertGreaterEqual(result, 0.0)

    def test_specific_known_scenario(self):
        # This test simulates a specific scenario where we know the expected outcome
        users = [1, 2, 3, 4]
        friendships = [(1, 2), (2, 3), (3, 4)]
        
        # Two server locations: one clearly better for all users
        potential_server_locations = [(0.0, 0.0), (1000.0, 1000.0)]
        num_servers = 1
        
        def mock_latency(coord1, coord2):
            # The first location gives a fixed low latency, second location gives high latency
            if coord1 == (0.0, 0.0) and coord2 == (0.0, 0.0):
                return 10.0
            elif coord1 == (1000.0, 1000.0) and coord2 == (1000.0, 1000.0):
                return 500.0
            else:
                return 1000.0

        result = optimize_network_latency(users, friendships, potential_server_locations, num_servers, mock_latency)
        # The optimal solution should place the server at (0.0, 0.0)
        # All users would be assigned to this server with a latency of 10.0
        self.assertEqual(result, 10.0)

if __name__ == '__main__':
    unittest.main()