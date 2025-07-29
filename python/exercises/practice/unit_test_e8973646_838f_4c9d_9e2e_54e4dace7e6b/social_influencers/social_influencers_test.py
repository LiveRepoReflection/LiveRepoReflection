import unittest
from social_influencers import find_top_influencers


class SocialInfluencersTest(unittest.TestCase):
    def test_small_network(self):
        # Small network with clear influence hierarchy
        edges = [
            (1, 2, "sports", 0.8),
            (1, 3, "technology", 0.6),
            (2, 3, "sports", 0.9),
            (3, 2, "politics", 0.7)
        ]
        user_credibility = {
            1: 0.7,
            2: 0.9,
            3: 0.5
        }
        damping_factor = 0.85
        tolerance = 1e-6
        k = 2
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 2)
        # User 2 should be the top influencer based on the network structure and credibility
        self.assertEqual(result[0], 2)
        # The second top influencer should be either 1 or 3, but given the parameters, likely 1
        self.assertIn(result[1], [1, 3])

    def test_larger_network(self):
        # More complex network with multiple topics and varied interaction strengths
        edges = [
            (1, 2, "sports", 0.8),
            (1, 3, "technology", 0.6),
            (1, 4, "politics", 0.5),
            (1, 5, "entertainment", 0.7),
            (2, 3, "sports", 0.9),
            (2, 5, "politics", 0.4),
            (3, 2, "politics", 0.7),
            (3, 4, "technology", 0.8),
            (4, 5, "entertainment", 0.9),
            (5, 1, "sports", 0.5),
            (5, 3, "politics", 0.6)
        ]
        user_credibility = {
            1: 0.7,
            2: 0.9,
            3: 0.8,
            4: 0.5,
            5: 0.6
        }
        damping_factor = 0.85
        tolerance = 1e-6
        k = 3
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 3)
        # All results should be valid user IDs
        for user_id in result:
            self.assertIn(user_id, user_credibility.keys())
        # No duplicates in result
        self.assertEqual(len(result), len(set(result)))

    def test_disconnected_network(self):
        # Network with two disconnected components
        edges = [
            (1, 2, "sports", 0.8),
            (2, 1, "politics", 0.7),
            (3, 4, "technology", 0.9),
            (4, 3, "entertainment", 0.6)
        ]
        user_credibility = {
            1: 0.7,
            2: 0.9,
            3: 0.8,
            4: 0.5
        }
        damping_factor = 0.85
        tolerance = 1e-6
        k = 3
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 3)
        # Should include users from both components
        self.assertTrue(set(result).intersection({1, 2}) and set(result).intersection({3, 4}))

    def test_user_with_zero_credibility(self):
        # Network with a user having zero credibility
        edges = [
            (1, 2, "sports", 0.8),
            (1, 3, "technology", 0.6),
            (2, 3, "sports", 0.9),
            (3, 2, "politics", 0.7)
        ]
        user_credibility = {
            1: 0.0,  # Zero credibility
            2: 0.9,
            3: 0.5
        }
        damping_factor = 0.85
        tolerance = 1e-6
        k = 3
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 3)
        # User 1 should be ranked lower due to zero credibility
        self.assertNotEqual(result[0], 1)

    def test_high_precision_requirement(self):
        # Test with very low tolerance for high precision
        edges = [
            (1, 2, "sports", 0.8),
            (2, 3, "politics", 0.7),
            (3, 1, "technology", 0.6)
        ]
        user_credibility = {
            1: 0.7,
            2: 0.9,
            3: 0.8
        }
        damping_factor = 0.99  # High damping factor
        tolerance = 1e-10  # Very low tolerance
        k = 3
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 3)
        # Should converge despite tight tolerance
        self.assertSetEqual(set(result), {1, 2, 3})

    def test_large_k_value(self):
        # Test when k is larger than the number of users
        edges = [
            (1, 2, "sports", 0.8),
            (2, 1, "politics", 0.7)
        ]
        user_credibility = {
            1: 0.7,
            2: 0.9
        }
        damping_factor = 0.85
        tolerance = 1e-6
        k = 5  # Larger than number of users
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 2)  # Should return all available users
        self.assertSetEqual(set(result), {1, 2})

    def test_multiple_topics_per_user_pair(self):
        # Test when users interact on multiple topics
        edges = [
            (1, 2, "sports", 0.3),
            (1, 2, "politics", 0.4),
            (1, 2, "technology", 0.2),
            (2, 1, "entertainment", 0.5),
            (2, 1, "sports", 0.3)
        ]
        user_credibility = {
            1: 0.7,
            2: 0.9
        }
        damping_factor = 0.85
        tolerance = 1e-6
        k = 2
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 2)
        self.assertSetEqual(set(result), {1, 2})
        # User with higher credibility should be ranked higher
        self.assertEqual(result[0], 2)

    def test_edge_case_single_user(self):
        # Test with only one user
        edges = []
        user_credibility = {1: 0.7}
        damping_factor = 0.85
        tolerance = 1e-6
        k = 1
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 1)

    def test_edge_case_empty_network(self):
        # Test with no users and no edges
        edges = []
        user_credibility = {}
        damping_factor = 0.85
        tolerance = 1e-6
        k = 5
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 0)  # Should return empty list

    def test_complex_network_with_many_topics(self):
        # Complex network with many topics to test topic weight calculations
        edges = [
            (1, 2, "sports", 0.3),
            (1, 3, "technology", 0.4),
            (1, 4, "politics", 0.2),
            (1, 5, "entertainment", 0.1),
            (2, 3, "fashion", 0.5),
            (2, 4, "food", 0.3),
            (3, 5, "travel", 0.7),
            (4, 1, "music", 0.6),
            (5, 2, "art", 0.4),
            (3, 1, "literature", 0.2),
            (4, 2, "science", 0.5),
            (5, 3, "history", 0.3),
            (2, 1, "games", 0.1),
            (3, 4, "business", 0.8)
        ]
        user_credibility = {
            1: 0.7,
            2: 0.9,
            3: 0.8,
            4: 0.6,
            5: 0.5
        }
        damping_factor = 0.85
        tolerance = 1e-6
        k = 3
        
        result = find_top_influencers(edges, user_credibility, damping_factor, tolerance, k)
        self.assertEqual(len(result), 3)
        # All results should be valid user IDs
        for user_id in result:
            self.assertIn(user_id, user_credibility.keys())
        # No duplicates in result
        self.assertEqual(len(result), len(set(result)))


if __name__ == '__main__':
    unittest.main()