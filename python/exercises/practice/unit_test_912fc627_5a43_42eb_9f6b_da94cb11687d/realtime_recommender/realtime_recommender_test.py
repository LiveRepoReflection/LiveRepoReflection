import unittest
from unittest.mock import patch
import time
import numpy as np
from realtime_recommender import RealtimeRecommender, get_recommendations

class RealtimeRecommenderTest(unittest.TestCase):
    def setUp(self):
        # Reset the recommender before each test
        self.recommender = RealtimeRecommender()
        
        # Sample product catalog
        self.product_catalog = {
            1: {"product_id": 1, "features": [0.1, 0.2, 0.3]},
            2: {"product_id": 2, "features": [0.2, 0.3, 0.4]},
            3: {"product_id": 3, "features": [0.3, 0.4, 0.5]},
            4: {"product_id": 4, "features": [0.4, 0.5, 0.6]},
            5: {"product_id": 5, "features": [0.5, 0.6, 0.7]},
            6: {"product_id": 6, "features": [0.6, 0.7, 0.8]},
            7: {"product_id": 7, "features": [0.7, 0.8, 0.9]},
            8: {"product_id": 8, "features": [0.8, 0.9, 1.0]},
            9: {"product_id": 9, "features": [0.9, 1.0, 0.1]},
            10: {"product_id": 10, "features": [1.0, 0.1, 0.2]}
        }
        
        # Add products to recommender
        for product_id, product in self.product_catalog.items():
            self.recommender.add_product(product)
    
    def test_empty_recommendations(self):
        """Test that recommendations for a new user are based only on product similarity."""
        # New user, no interactions
        recommendations = self.recommender.get_recommendations(999, 1, 3)
        
        # Should return recommendations based on product similarity
        self.assertEqual(len(recommendations), 3)
        
        # First recommendation should be the most similar product to product 1
        # Product similarity should be based on cosine similarity
        similarities = []
        for pid in range(2, 11):
            sim = np.dot(self.product_catalog[1]["features"], self.product_catalog[pid]["features"]) / (
                np.linalg.norm(self.product_catalog[1]["features"]) * 
                np.linalg.norm(self.product_catalog[pid]["features"])
            )
            similarities.append((pid, sim))
        
        top_similar = sorted(similarities, key=lambda x: x[1], reverse=True)[:3]
        expected_recommendations = [pid for pid, _ in top_similar]
        
        # Check if recommendations match expected top similar products
        # Order might vary due to implementation details, so we just check if sets are equal
        self.assertEqual(set(recommendations), set(expected_recommendations))
    
    def test_user_interactions(self):
        """Test that user interactions affect recommendations."""
        # Add some user interactions
        self.recommender.add_interaction({
            "user_id": 123,
            "product_id": 3,
            "event_type": "view",
            "timestamp": int(time.time())
        })
        
        self.recommender.add_interaction({
            "user_id": 123,
            "product_id": 5,
            "event_type": "cart",
            "timestamp": int(time.time())
        })
        
        self.recommender.add_interaction({
            "user_id": 123,
            "product_id": 7,
            "event_type": "purchase",
            "timestamp": int(time.time())
        })
        
        # Get recommendations
        recommendations = self.recommender.get_recommendations(123, 1, 5)
        
        # Should return 5 recommendations
        self.assertEqual(len(recommendations), 5)
        
        # Products 3, 5, and 7 should be ranked higher due to user interactions
        # Exact order depends on implementation, but they should appear before others
        interaction_products = {3, 5, 7}
        non_interaction_products = set(range(1, 11)) - interaction_products - {1}  # Exclude viewed product
        
        # Count products from each set in the recommendations
        interaction_count = sum(1 for pid in recommendations if pid in interaction_products)
        
        # Assert that at least some of the interaction products are in the recommendations
        self.assertGreater(interaction_count, 0)
    
    def test_event_type_weighting(self):
        """Test that different event types have different weights."""
        # User 1 views product 2
        self.recommender.add_interaction({
            "user_id": 1,
            "product_id": 2,
            "event_type": "view",
            "timestamp": int(time.time())
        })
        
        # User 2 adds product 2 to cart
        self.recommender.add_interaction({
            "user_id": 2,
            "product_id": 2,
            "event_type": "cart",
            "timestamp": int(time.time())
        })
        
        # User 3 purchases product 2
        self.recommender.add_interaction({
            "user_id": 3,
            "product_id": 2,
            "event_type": "purchase",
            "timestamp": int(time.time())
        })
        
        # Get recommendations for each user
        rec1 = self.recommender.get_recommendations(1, 1, 3)
        rec2 = self.recommender.get_recommendations(2, 1, 3)
        rec3 = self.recommender.get_recommendations(3, 1, 3)
        
        # All users should have product 2 in their recommendations,
        # but its position might vary based on the event type weight
        # We can't assert exact positions without knowing the implementation,
        # but we can check that it's in the recommendations
        self.assertIn(2, rec1)
        self.assertIn(2, rec2)
        self.assertIn(2, rec3)
    
    def test_time_decay(self):
        """Test that older interactions have less influence."""
        # Add an old interaction
        old_time = int(time.time()) - 3600 * 24 * 7  # 7 days ago
        self.recommender.add_interaction({
            "user_id": 456,
            "product_id": 4,
            "event_type": "purchase",
            "timestamp": old_time
        })
        
        # Add a recent interaction
        recent_time = int(time.time())
        self.recommender.add_interaction({
            "user_id": 456,
            "product_id": 8,
            "event_type": "view",  # Even though it's just a view
            "timestamp": recent_time
        })
        
        # Get recommendations
        recommendations = self.recommender.get_recommendations(456, 1, 3)
        
        # Recent interaction (product 8) should be ranked higher than old interaction (product 4)
        # even though the old one was a purchase and the recent one was just a view
        # This depends on how time decay is implemented, so the assertion might need adjustment
        if 4 in recommendations and 8 in recommendations:
            idx4 = recommendations.index(4)
            idx8 = recommendations.index(8)
            self.assertLess(idx8, idx4)  # 8 should come before 4
    
    def test_cold_start(self):
        """Test handling of new users and products."""
        # New user
        new_user_recommendations = self.recommender.get_recommendations(999, 1, 3)
        
        # Should still return recommendations based on product similarity
        self.assertEqual(len(new_user_recommendations), 3)
        
        # Add a new product without any interactions
        new_product = {"product_id": 11, "features": [0.1, 0.1, 0.1]}
        self.recommender.add_product(new_product)
        
        # Get recommendations for the new product
        new_product_recommendations = self.recommender.get_recommendations(123, 11, 3)
        
        # Should return recommendations based on product similarity
        self.assertEqual(len(new_product_recommendations), 3)
    
    def test_k_limit(self):
        """Test different values of k."""
        # k = 1
        rec1 = self.recommender.get_recommendations(123, 1, 1)
        self.assertEqual(len(rec1), 1)
        
        # k = 5
        rec5 = self.recommender.get_recommendations(123, 1, 5)
        self.assertEqual(len(rec5), 5)
        
        # k = 100 (maximum allowed)
        rec100 = self.recommender.get_recommendations(123, 1, 100)
        # Should return at most 9 recommendations (all products except the viewed one)
        self.assertEqual(len(rec100), 9)
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Invalid user_id
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations(-1, 1, 3)
        
        # Invalid product_id
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations(123, 999, 3)  # Product doesn't exist
        
        # Invalid k
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations(123, 1, 0)  # k must be positive
        
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations(123, 1, 101)  # k must be <= 100
    
    def test_function_wrapper(self):
        """Test the get_recommendations wrapper function."""
        with patch('realtime_recommender.RealtimeRecommender.get_recommendations') as mock_get:
            mock_get.return_value = [2, 3, 4]
            result = get_recommendations(123, 1, 3)
            mock_get.assert_called_once_with(123, 1, 3)
            self.assertEqual(result, [2, 3, 4])
    
    def test_large_scale(self):
        """Test with a larger number of products and interactions."""
        # Create a new recommender for this test
        large_recommender = RealtimeRecommender()
        
        # Add 1000 products
        for i in range(1, 1001):
            features = [np.random.random() for _ in range(10)]
            large_recommender.add_product({"product_id": i, "features": features})
        
        # Add 10000 interactions
        current_time = int(time.time())
        for i in range(10000):
            user_id = np.random.randint(1, 101)  # 100 users
            product_id = np.random.randint(1, 1001)  # 1000 products
            event_type = np.random.choice(["view", "cart", "purchase"], p=[0.7, 0.2, 0.1])
            timestamp = current_time - np.random.randint(0, 86400 * 30)  # Up to 30 days ago
            
            large_recommender.add_interaction({
                "user_id": user_id,
                "product_id": product_id,
                "event_type": event_type,
                "timestamp": timestamp
            })
        
        # Test that recommendations are returned quickly
        start_time = time.time()
        recommendations = large_recommender.get_recommendations(50, 500, 10)
        end_time = time.time()
        
        # Should return 10 recommendations
        self.assertEqual(len(recommendations), 10)
        
        # Should take less than 100ms (0.1 seconds)
        self.assertLess(end_time - start_time, 0.1)

if __name__ == '__main__':
    unittest.main()