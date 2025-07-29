import unittest
from unittest.mock import MagicMock
from social_recommend import recommend_users

class TestSocialRecommend(unittest.TestCase):
    def setUp(self):
        # Create a basic social network structure for testing
        self.network = {
            # user_id: (followers, followees)
            1: ({2, 3, 4}, {5, 6}),
            2: ({3, 5}, {1, 6, 7}),
            3: ({5, 6}, {1, 2, 5}),
            4: ({2, 7}, {1, 8}),
            5: ({6, 7}, {2, 3, 8}),
            6: ({5, 7}, {1, 2, 3}),
            7: ({8}, {2, 5, 6}),
            8: ({4, 5}, {4, 7}),
            9: ({}, {10}),
            10: ({9}, {}),
        }
        
        self.get_neighbors = MagicMock(side_effect=lambda user_id: self.network.get(user_id, (set(), set())))
    
    def test_basic_recommendation(self):
        """Test basic recommendation functionality."""
        # User 1 follows 5 and 6, should recommend users like 2, 3, 7, 8
        recommendations = recommend_users(1, 4, self.get_neighbors)
        self.assertEqual(len(recommendations), 4)
        # Should not recommend users that user 1 already follows
        self.assertNotIn(5, recommendations)
        self.assertNotIn(6, recommendations)
        # Should not recommend the user themselves
        self.assertNotIn(1, recommendations)
    
    def test_ordered_recommendations(self):
        """Test that recommendations are ordered by interest score."""
        # Based on our network, for user 1, interest should be highest for users like 2 and 3
        recommendations = recommend_users(1, 5, self.get_neighbors)
        # First recommendations should have higher interest scores
        # This test depends on the specific implementation of the interest metric
        self.assertTrue(set([2, 3]).issubset(set(recommendations[:3])))
    
    def test_fewer_than_k_recommendations(self):
        """Test when fewer than k recommendations are possible."""
        # User 9 only has connections to user 10, and has limited recommendation options
        recommendations = recommend_users(9, 5, self.get_neighbors)
        # Should return all possible recommendations, which is less than k
        self.assertLess(len(recommendations), 5)
    
    def test_no_connections(self):
        """Test with a user that has no connections."""
        # Create a user with no connections
        self.network[11] = (set(), set())
        recommendations = recommend_users(11, 3, self.get_neighbors)
        # Should return an empty list or a list with less than k recommendations
        self.assertLessEqual(len(recommendations), 3)
    
    def test_api_call_efficiency(self):
        """Test that the solution minimizes API calls."""
        self.get_neighbors.reset_mock()
        recommend_users(1, 3, self.get_neighbors)
        # Check that get_neighbors wasn't called excessively
        # The exact number will depend on the implementation, but should be optimized
        # As a baseline, we shouldn't need to query every user in the network
        self.assertLess(self.get_neighbors.call_count, len(self.network))
    
    def test_large_k(self):
        """Test with a k larger than possible recommendations."""
        recommendations = recommend_users(1, 100, self.get_neighbors)
        # Should return all possible recommendations, which is less than k
        self.assertLess(len(recommendations), 100)
        # Should not contain duplicates
        self.assertEqual(len(recommendations), len(set(recommendations)))
    
    def test_isolated_user(self):
        """Test with an isolated user that has no followers or followees."""
        self.network[12] = (set(), set())
        recommendations = recommend_users(12, 5, self.get_neighbors)
        # Should handle this case gracefully
        self.assertEqual(len(recommendations), 0)
    
    def test_non_existent_user(self):
        """Test with a user that doesn't exist in the network."""
        recommendations = recommend_users(999, 5, self.get_neighbors)
        # Should handle this case gracefully
        self.assertEqual(len(recommendations), 0)
    
    def test_recommendation_uniqueness(self):
        """Test that recommendations don't include followees or the user themselves."""
        user_id = 3  # User 3 follows 1, 2, 5
        recommendations = recommend_users(user_id, 5, self.get_neighbors)
        # Check that user_id itself is not in recommendations
        self.assertNotIn(user_id, recommendations)
        # Check that user's followees are not in recommendations
        followees = self.network[user_id][1]
        for followee in followees:
            self.assertNotIn(followee, recommendations)
    
    def test_interest_score_calculation(self):
        """Test that interest scores are calculated correctly."""
        # This test depends on the specific implementation of the interest metric
        # We'll focus on user 4, who follows user 1 and 8
        # User 4 should have high interest in user 5 (common connections with 8)
        recommendations = recommend_users(4, 3, self.get_neighbors)
        # User 5 should be recommended with high priority
        self.assertIn(5, recommendations[:2])

if __name__ == '__main__':
    unittest.main()