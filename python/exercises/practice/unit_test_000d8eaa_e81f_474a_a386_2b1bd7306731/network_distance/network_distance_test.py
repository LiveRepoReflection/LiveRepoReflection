import unittest
from network_distance import network_distance

class MockNetworkData:
    def __init__(self):
        self.query_count = 0
        self.network = {
            1: ([2, 3], [4]),     # User 1 follows 2, 3 and is followed by 4
            2: ([5], [1]),        # User 2 follows 5 and is followed by 1
            3: ([], [1]),         # User 3 follows no one and is followed by 1
            4: ([1], []),         # User 4 follows 1 and is followed by no one
            5: ([], [2]),         # User 5 follows no one and is followed by 2
            6: ([7, 8], []),      # User 6 follows 7, 8 and is followed by no one
            7: ([9], [6]),        # User 7 follows 9 and is followed by 6
            8: ([10], [6]),       # User 8 follows 10 and is followed by 6
            9: ([], [7]),         # User 9 follows no one and is followed by 7
            10: ([], [8]),        # User 10 follows no one and is followed by 8
            11: ([12], []),       # User 11 follows 12 and is followed by no one
            12: ([11], [11]),     # User 12 follows 11 and is followed by 11 (cycle)
            # Isolated nodes
            100: ([], []),        # User 100 has no connections
            # Big graph section
            1000: ([i for i in range(1001, 1101)], []), # User 1000 follows 100 users
        }
        # Add 100 users that follow user 2000
        self.network[2000] = ([], [i for i in range(2001, 2101)])
        
        # Create a complex web of relationships
        for i in range(1001, 1101):
            self.network[i] = ([], [1000])
        
        for i in range(2001, 2101):
            self.network[i] = ([2000], [])

    def query_user(self, user_id):
        """Mock implementation of query_user function"""
        self.query_count += 1
        if user_id in self.network:
            return self.network[user_id]
        return None

class NetworkDistanceTest(unittest.TestCase):
    def setUp(self):
        self.mock_data = MockNetworkData()
        
    def test_degree_zero(self):
        """Test with k=0 (only the start user)"""
        result = network_distance(1, 0, self.mock_data.query_user, 1000)
        self.assertEqual(result, {1})
        self.assertLessEqual(self.mock_data.query_count, 1)
        
    def test_basic_example(self):
        """Test the basic example from the problem description"""
        self.mock_data.query_count = 0
        result = network_distance(1, 2, self.mock_data.query_user, 10)
        self.assertEqual(result, {1, 2, 3, 4, 5})
        self.assertLessEqual(self.mock_data.query_count, 5)
        
    def test_invalid_start_user(self):
        """Test with an invalid start user ID"""
        result = network_distance(999, 2, self.mock_data.query_user, 10)
        self.assertEqual(result, set())
        self.assertEqual(self.mock_data.query_count, 1)
        
    def test_isolated_user(self):
        """Test with an isolated user (no connections)"""
        self.mock_data.query_count = 0
        result = network_distance(100, 3, self.mock_data.query_user, 10)
        self.assertEqual(result, {100})
        self.assertEqual(self.mock_data.query_count, 1)
        
    def test_cyclic_relationship(self):
        """Test with a cycle in the graph"""
        self.mock_data.query_count = 0
        result = network_distance(11, 3, self.mock_data.query_user, 10)
        self.assertEqual(result, {11, 12})
        self.assertLessEqual(self.mock_data.query_count, 3)
        
    def test_large_degree(self):
        """Test with a large degree of separation"""
        self.mock_data.query_count = 0
        result = network_distance(6, 3, self.mock_data.query_user, 10)
        self.assertEqual(result, {6, 7, 8, 9, 10})
        self.assertLessEqual(self.mock_data.query_count, 5)
        
    def test_query_limit(self):
        """Test with a query limit that's lower than needed to explore fully"""
        self.mock_data.query_count = 0
        # With a limit of 2, we can't explore all connections from user 1
        result = network_distance(1, 2, self.mock_data.query_user, 2)
        self.assertLessEqual(self.mock_data.query_count, 2)
        
    def test_large_followers_list(self):
        """Test with a user that has many followers"""
        self.mock_data.query_count = 0
        result = network_distance(2000, 1, self.mock_data.query_user, 10)
        # Should include 2000 and all its followers (2001-2100)
        expected = {2000} | set(range(2001, 2101))
        self.assertEqual(result, expected)
        # Should need at most 2 queries: one for user 2000 and possibly one extra
        self.assertLessEqual(self.mock_data.query_count, 2)
        
    def test_large_following_list(self):
        """Test with a user that follows many others"""
        self.mock_data.query_count = 0
        result = network_distance(1000, 1, self.mock_data.query_user, 10)
        # Should include 1000 and all users it follows (1001-1100)
        expected = {1000} | set(range(1001, 1101))
        self.assertEqual(result, expected)
        # Should need at most 2 queries: one for user 1000 and possibly one extra
        self.assertLessEqual(self.mock_data.query_count, 2)
        
    def test_query_efficiency(self):
        """Test that the solution doesn't make unnecessary queries"""
        self.mock_data.query_count = 0
        network_distance(1, 2, self.mock_data.query_user, 1000)
        # A naive BFS or DFS would query each user exactly once
        # An optimized solution might query less
        self.assertLessEqual(self.mock_data.query_count, 5)

if __name__ == '__main__':
    unittest.main()