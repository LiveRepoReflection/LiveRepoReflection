import unittest
from unittest.mock import Mock, patch
from social_degree import calculate_k_degree_centrality


class SocialDegreeTest(unittest.TestCase):
    def test_basic_case(self):
        # User 1 is connected to users 2, 3, and 4.
        # User 2 is connected to users 1 and 5.
        # User 3 is connected to user 1.
        # User 4 is connected to user 1.
        # User 5 is connected to user 2.
        def mock_get_neighbors(user_id):
            neighbors = {
                1: [2, 3, 4],
                2: [1, 5],
                3: [1],
                4: [1],
                5: [2],
            }
            return iter(neighbors.get(user_id, []))
        
        # For user 1 with k=2, should return 4 (users 2, 3, 4, 5)
        self.assertEqual(calculate_k_degree_centrality(1, 2, mock_get_neighbors), 4)
        # For user 1 with k=1, should return 3 (users 2, 3, 4)
        self.assertEqual(calculate_k_degree_centrality(1, 1, mock_get_neighbors), 3)
        # For user 2 with k=2, should return 3 (users 1, 3, 4, 5)
        self.assertEqual(calculate_k_degree_centrality(2, 2, mock_get_neighbors), 4)
        # For user 5 with k=3, should return 4 (users 1, 2, 3, 4)
        self.assertEqual(calculate_k_degree_centrality(5, 3, mock_get_neighbors), 4)

    def test_cyclic_graph(self):
        # Test with a cyclic graph
        def mock_get_neighbors(user_id):
            neighbors = {
                1: [2, 3],
                2: [1, 4],
                3: [1, 5],
                4: [2, 6],
                5: [3, 6],
                6: [4, 5],
            }
            return iter(neighbors.get(user_id, []))
        
        # For user 1 with k=3, should return all other nodes (2-6)
        self.assertEqual(calculate_k_degree_centrality(1, 3, mock_get_neighbors), 5)
        # For user 1 with k=1, should return only direct connections
        self.assertEqual(calculate_k_degree_centrality(1, 1, mock_get_neighbors), 2)
        # For user 1 with k=2, should return 2nd level connections too
        self.assertEqual(calculate_k_degree_centrality(1, 2, mock_get_neighbors), 4)  # users 2, 3, 4, 5

    def test_disconnected_graph(self):
        def mock_get_neighbors(user_id):
            neighbors = {
                1: [2, 3],
                2: [1],
                3: [1],
                4: [5],
                5: [4],
            }
            return iter(neighbors.get(user_id, []))
        
        # For user 1 with k=10, should return only connected components (2, 3)
        self.assertEqual(calculate_k_degree_centrality(1, 10, mock_get_neighbors), 2)
        # For user 4 with k=10, should return only its component (5)
        self.assertEqual(calculate_k_degree_centrality(4, 10, mock_get_neighbors), 1)

    def test_duplicate_connections(self):
        def mock_get_neighbors(user_id):
            # Returning duplicates to simulate real-world data issues
            neighbors = {
                1: [2, 2, 3, 3],
                2: [1, 1, 4, 4],
                3: [1, 1],
                4: [2, 2],
            }
            return iter(neighbors.get(user_id, []))
        
        # Should handle duplicates correctly
        self.assertEqual(calculate_k_degree_centrality(1, 2, mock_get_neighbors), 3)  # users 2, 3, 4

    def test_large_k_values(self):
        def mock_get_neighbors(user_id):
            neighbors = {
                1: [2],
                2: [3],
                3: [4],
                4: [5],
                5: [],
            }
            return iter(neighbors.get(user_id, []))
        
        # With k=10, should traverse the entire path
        self.assertEqual(calculate_k_degree_centrality(1, 10, mock_get_neighbors), 4)  # users 2, 3, 4, 5
        # With k=3, should only reach user 4
        self.assertEqual(calculate_k_degree_centrality(1, 3, mock_get_neighbors), 3)  # users 2, 3, 4

    def test_empty_neighbors(self):
        def mock_get_neighbors(user_id):
            return iter([])
        
        # If a user has no connections, centrality should be 0
        self.assertEqual(calculate_k_degree_centrality(1, 5, mock_get_neighbors), 0)

    def test_call_optimization(self):
        # Test that get_neighbors is called only when necessary
        mock_get_neighbors = Mock(side_effect=lambda user_id: iter([]))
        
        calculate_k_degree_centrality(1, 5, mock_get_neighbors)
        # Should call get_neighbors once for user 1
        self.assertEqual(mock_get_neighbors.call_count, 1)

        # More complex scenario
        mock_get_neighbors.reset_mock()
        mock_get_neighbors.side_effect = lambda user_id: iter([2]) if user_id == 1 else iter([])
        
        calculate_k_degree_centrality(1, 5, mock_get_neighbors)
        # Should call get_neighbors for user 1 and user 2
        self.assertEqual(mock_get_neighbors.call_count, 2)

    @patch('builtins.print')
    def test_invalid_k_values(self, mock_print):
        def mock_get_neighbors(user_id):
            return iter([])

        # k must be at least 1
        with self.assertRaises(ValueError):
            calculate_k_degree_centrality(1, 0, mock_get_neighbors)
        
        # k must not exceed 10
        with self.assertRaises(ValueError):
            calculate_k_degree_centrality(1, 11, mock_get_neighbors)

if __name__ == '__main__':
    unittest.main()