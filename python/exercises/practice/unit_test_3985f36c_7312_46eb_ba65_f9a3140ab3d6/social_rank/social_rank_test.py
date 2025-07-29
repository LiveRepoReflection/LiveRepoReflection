import unittest
from unittest.mock import Mock
from social_rank import rank_users

class TestSocialRank(unittest.TestCase):
    def test_single_node_network(self):
        # Mock network with a single node (only the starting node)
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: (
            {"followers": [], "followees": []} if user_id == 1 else None
        )
        
        result = rank_users(1, mock_network, 1, 1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 1)  # User ID should be 1
        self.assertGreaterEqual(result[0][1], 0)  # Score should be non-negative
        self.assertEqual(mock_network.call_count, 1)  # Should make exactly one call

    def test_simple_star_network(self):
        # Create a star network where central node (1) is followed by all others
        network_data = {
            1: {"followers": [2, 3, 4, 5], "followees": []},
            2: {"followers": [], "followees": [1]},
            3: {"followers": [], "followees": [1]},
            4: {"followers": [], "followees": [1]},
            5: {"followers": [], "followees": [1]},
        }
        
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: network_data.get(user_id)
        
        result = rank_users(1, mock_network, 2, 5)
        
        # Node 1 should have highest score as it has most followers
        self.assertEqual(result[0][0], 1)
        
        # Check all users are ranked
        self.assertEqual(len(result), 5)
        ranked_users = [user_id for user_id, _ in result]
        self.assertSetEqual(set(ranked_users), {1, 2, 3, 4, 5})

    def test_directed_cycle(self):
        # Create a cycle where 1 -> 2 -> 3 -> 1
        network_data = {
            1: {"followers": [3], "followees": [2]},
            2: {"followers": [1], "followees": [3]},
            3: {"followers": [2], "followees": [1]},
        }
        
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: network_data.get(user_id)
        
        result = rank_users(1, mock_network, 5, 3)
        
        # All users should be ranked
        self.assertEqual(len(result), 3)
        ranked_users = [user_id for user_id, _ in result]
        self.assertSetEqual(set(ranked_users), {1, 2, 3})
        
        # All users should have equal scores (in this particular structure)
        # If this isn't true for your algorithm, adjust this test
        scores = [score for _, score in result]
        self.assertAlmostEqual(scores[0], scores[1], places=6)
        self.assertAlmostEqual(scores[1], scores[2], places=6)

    def test_max_hops_constraint(self):
        # Create a chain: 1 -> 2 -> 3 -> 4 -> 5
        network_data = {
            1: {"followers": [], "followees": [2]},
            2: {"followers": [1], "followees": [3]},
            3: {"followers": [2], "followees": [4]},
            4: {"followers": [3], "followees": [5]},
            5: {"followers": [4], "followees": []},
        }
        
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: network_data.get(user_id)
        
        # Only allow 2 hops, so should only see users 1, 2, and 3
        result = rank_users(1, mock_network, 2, 5)
        
        ranked_users = [user_id for user_id, _ in result]
        self.assertTrue(all(user_id in [1, 2, 3] for user_id in ranked_users))
        self.assertLessEqual(mock_network.call_count, 5)  # At most 5 calls (1+followers+followees)

    def test_max_users_constraint(self):
        # Create a network where 1 can reach many users
        network_data = {
            1: {"followers": [], "followees": [2, 3, 4, 5, 6]},
            2: {"followers": [1], "followees": []},
            3: {"followers": [1], "followees": []},
            4: {"followers": [1], "followees": []},
            5: {"followers": [1], "followees": []},
            6: {"followers": [1], "followees": []},
        }
        
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: network_data.get(user_id)
        
        # Limit to 3 users
        result = rank_users(1, mock_network, 10, 3)
        
        self.assertLessEqual(len(result), 3)

    def test_null_data_handling(self):
        # Network with some missing data
        network_data = {
            1: {"followers": [2, 3], "followees": [4]},
            2: {"followers": [], "followees": [1]},
            # User 3 data is missing
            4: {"followers": [1], "followees": []},
        }
        
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: network_data.get(user_id)
        
        result = rank_users(1, mock_network, 2, 10)
        
        # Should still handle the request and include valid users
        self.assertGreaterEqual(len(result), 3)  # At least 1, 2, and 4 should be ranked
        ranked_users = [user_id for user_id, _ in result]
        self.assertTrue(all(user_id in ranked_users for user_id in [1, 2, 4]))

    def test_complex_network(self):
        # More complex network to simulate real-world scenario
        network_data = {
            1: {"followers": [2, 3, 4], "followees": [5, 6]},
            2: {"followers": [3, 7], "followees": [1, 3]},
            3: {"followers": [1, 2, 5], "followees": [2, 4]},
            4: {"followers": [3, 6], "followees": [1, 5]},
            5: {"followers": [1, 4, 8], "followees": [3, 9]},
            6: {"followers": [1, 9], "followees": [4, 10]},
            7: {"followers": [8, 10], "followees": [2]},
            8: {"followers": [9], "followees": [5, 7]},
            9: {"followers": [5, 10], "followees": [6, 8]},
            10: {"followers": [6], "followees": [7, 9]},
        }
        
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: network_data.get(user_id)
        
        result = rank_users(1, mock_network, 3, 10)
        
        # Verify results format
        self.assertLessEqual(len(result), 10)
        for user_score in result:
            self.assertEqual(len(user_score), 2)
            user_id, score = user_score
            self.assertIsInstance(user_id, int)
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0)
        
        # Make sure results are sorted by score (descending)
        scores = [score for _, score in result]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Check for tie-breaking by user_id (if any ties exist)
        for i in range(len(scores) - 1):
            if scores[i] == scores[i+1]:
                self.assertLess(result[i][0], result[i+1][0])

    def test_disconnected_user(self):
        # Network with a disconnected user
        network_data = {
            1: {"followers": [], "followees": []},
            2: {"followers": [3], "followees": [3]},
            3: {"followers": [2], "followees": [2]},
        }
        
        mock_network = Mock()
        mock_network.side_effect = lambda user_id: network_data.get(user_id)
        
        result = rank_users(1, mock_network, 2, 3)
        
        # Should only include user 1
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 1)

    def test_dynamic_changing_network(self):
        # Simulate a network that changes between calls
        call_count = 0
        
        def dynamic_network(user_id):
            nonlocal call_count
            call_count += 1
            
            if call_count <= 2:  # First 2 calls
                if user_id == 1:
                    return {"followers": [2], "followees": [3]}
                elif user_id == 2:
                    return {"followers": [], "followees": [1]}
                elif user_id == 3:
                    return {"followers": [1], "followees": []}
            else:  # Network changes after first 2 calls
                if user_id == 1:
                    return {"followers": [2, 4], "followees": [3, 5]}
                elif user_id == 2:
                    return {"followers": [], "followees": [1]}
                elif user_id == 3:
                    return {"followers": [1], "followees": []}
                elif user_id == 4:
                    return {"followers": [], "followees": [1]}
                elif user_id == 5:
                    return {"followers": [1], "followees": []}
            
            return None
        
        mock_network = Mock(side_effect=dynamic_network)
        
        result = rank_users(1, mock_network, 10, 10)
        
        # Verify a reasonable result was returned
        self.assertGreaterEqual(len(result), 1)

if __name__ == '__main__':
    unittest.main()