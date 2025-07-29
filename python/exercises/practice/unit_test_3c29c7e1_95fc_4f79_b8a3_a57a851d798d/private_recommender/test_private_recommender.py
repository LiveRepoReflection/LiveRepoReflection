import unittest
from unittest.mock import MagicMock
import random
import numpy as np
from private_recommender import generate_recommendations


class MockDataAccessor:
    def __init__(self, user_data):
        self.user_data = user_data
        
    def get_user_data(self, user_id):
        return self.user_data.get(user_id, {})


class TestPrivateRecommender(unittest.TestCase):
    
    def setUp(self):
        # Set random seed for reproducibility
        random.seed(42)
        np.random.seed(42)
        
        # Create a mock dataset
        self.num_users = 100
        self.num_items = 20
        self.user_data = {}
        
        # Generate random ratings (1-5) for each user, with some sparsity
        for user_id in range(self.num_users):
            user_ratings = {}
            # Each user rates about 70% of items
            for item_id in range(self.num_items):
                if random.random() < 0.7:
                    user_ratings[item_id] = random.randint(1, 5)
            self.user_data[user_id] = user_ratings
        
        # Create mock data accessor
        self.data_accessor = MockDataAccessor(self.user_data)
    
    def test_basic_recommendation(self):
        """Test that recommendations are generated for a user"""
        user_id = 0
        item_ids = list(range(self.num_items))
        epsilon = 1.0  # Reasonable privacy budget
        
        recommendations = generate_recommendations(user_id, item_ids, epsilon, self.data_accessor)
        
        # Check if recommendations are generated
        self.assertIsNotNone(recommendations)
        self.assertIsInstance(recommendations, list)
        
        # Check if recommended items are valid
        for item in recommendations:
            self.assertIn(item, item_ids)
        
        # Check if all recommended items are unique
        self.assertEqual(len(recommendations), len(set(recommendations)))
    
    def test_privacy_different_epsilon(self):
        """Test that different privacy budgets produce different recommendations"""
        user_id = 5
        item_ids = list(range(self.num_items))
        
        # Generate recommendations with different epsilon values
        recommendations_high_privacy = generate_recommendations(user_id, item_ids, 0.1, self.data_accessor)
        recommendations_low_privacy = generate_recommendations(user_id, item_ids, 2.0, self.data_accessor)
        
        # The recommendations should not be identical due to different noise levels
        # Note: This is probabilistic, so in rare cases this might fail
        self.assertNotEqual(recommendations_high_privacy, recommendations_low_privacy)
    
    def test_unseen_items_recommended(self):
        """Test that items not rated by the user can be recommended"""
        user_id = 10
        # Find items not rated by this user
        user_ratings = self.data_accessor.get_user_data(user_id)
        unrated_items = [item for item in range(self.num_items) if item not in user_ratings]
        
        # If user has rated all items, skip this test
        if not unrated_items:
            return
        
        # Generate recommendations
        epsilon = 1.0
        recommendations = generate_recommendations(user_id, list(range(self.num_items)), epsilon, self.data_accessor)
        
        # Check if at least one unrated item is recommended
        self.assertTrue(any(item in unrated_items for item in recommendations))
    
    def test_similar_users_get_similar_recommendations(self):
        """Test that similar users get somewhat similar recommendations"""
        # Create two almost identical users
        user1 = 42
        user2 = 43
        
        # Make their ratings identical except for one item
        identical_ratings = {item: 5 for item in range(5)}
        self.user_data[user1] = identical_ratings.copy()
        self.user_data[user2] = identical_ratings.copy()
        self.user_data[user2][0] = 4  # Slight difference
        
        # Generate recommendations
        epsilon = 1.0
        item_ids = list(range(self.num_items))
        recommendations1 = generate_recommendations(user1, item_ids, epsilon, self.data_accessor)
        recommendations2 = generate_recommendations(user2, item_ids, epsilon, self.data_accessor)
        
        # Calculate Jaccard similarity for the top 5 recommendations
        intersection = len(set(recommendations1[:5]).intersection(set(recommendations2[:5])))
        union = len(set(recommendations1[:5]).union(set(recommendations2[:5])))
        similarity = intersection / union if union > 0 else 0
        
        # Similar users should have somewhat similar recommendations
        # Due to differential privacy, we can't expect perfect similarity
        self.assertGreater(similarity, 0.2)
    
    def test_empty_recommendations(self):
        """Test behavior when no item_ids are provided"""
        user_id = 15
        item_ids = []
        epsilon = 1.0
        
        recommendations = generate_recommendations(user_id, item_ids, epsilon, self.data_accessor)
        
        # Should return an empty list
        self.assertEqual(recommendations, [])
    
    def test_unknown_user(self):
        """Test behavior for a user not in the dataset"""
        user_id = self.num_users + 100  # User ID not in dataset
        item_ids = list(range(self.num_items))
        epsilon = 1.0
        
        # Should not raise an exception
        recommendations = generate_recommendations(user_id, item_ids, epsilon, self.data_accessor)
        
        # Should return a valid list
        self.assertIsInstance(recommendations, list)
    
    def test_different_runs_different_results(self):
        """Test that differential privacy introduces randomness"""
        user_id = 20
        item_ids = list(range(self.num_items))
        epsilon = 0.5  # Moderate privacy
        
        # Run the recommendation algorithm multiple times
        results = []
        for _ in range(5):
            recommendations = generate_recommendations(user_id, item_ids, epsilon, self.data_accessor)
            results.append(recommendations)
        
        # At least some of the recommendation lists should be different due to added noise
        self.assertTrue(any(results[0] != results[i] for i in range(1, 5)))
    
    def test_epsilon_effect(self):
        """Test that smaller epsilon values introduce more noise"""
        user_id = 30
        item_ids = list(range(self.num_items))
        
        # Generate multiple recommendations with different epsilon values
        high_privacy_results = []
        low_privacy_results = []
        
        for _ in range(10):
            high_privacy_results.append(
                generate_recommendations(user_id, item_ids, 0.1, self.data_accessor))
            low_privacy_results.append(
                generate_recommendations(user_id, item_ids, 2.0, self.data_accessor))
        
        # Calculate variation within each set of results
        # More variation indicates more noise
        high_privacy_variation = len(set(tuple(r) for r in high_privacy_results))
        low_privacy_variation = len(set(tuple(r) for r in low_privacy_results))
        
        # Higher privacy (lower epsilon) should introduce more noise
        self.assertGreaterEqual(high_privacy_variation, low_privacy_variation)


if __name__ == '__main__':
    unittest.main()