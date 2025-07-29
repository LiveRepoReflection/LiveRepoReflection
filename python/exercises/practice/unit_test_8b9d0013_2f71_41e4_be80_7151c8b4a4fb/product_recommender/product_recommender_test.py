import unittest
import time
from product_recommender import RecommendationSystem

class RecommendationSystemTest(unittest.TestCase):
    def setUp(self):
        # Create an instance of the recommendation system.
        self.rs = RecommendationSystem()

        # Populate the product catalog with sample data.
        self.products = [
            {'product_id': 1, 'category': 'electronics', 'price': 299.99, 'other_features': {'brand': 'BrandA'}},
            {'product_id': 2, 'category': 'books', 'price': 19.99, 'other_features': {'author': 'AuthorA'}},
            {'product_id': 3, 'category': 'electronics', 'price': 99.99, 'other_features': {'brand': 'BrandB'}},
            {'product_id': 4, 'category': 'fashion', 'price': 49.99, 'other_features': {'brand': 'BrandC'}}
        ]
        for product in self.products:
            self.rs.update_catalog(product)

        # Set up a user profile with purchase and view history.
        self.user_profile = {
            'user_id': 100,
            'purchase_history': [1],
            'view_history': [2, 3],
            'other_features': {'location': 'NY'}
        }
        self.rs.update_user_profile(self.user_profile)

        # Simulate a stream of user events.
        self.events = [
            {'user_id': 100, 'event_type': 'view', 'product_id': 2, 'timestamp': 100000},
            {'user_id': 100, 'event_type': 'purchase', 'product_id': 1, 'timestamp': 100100},
            {'user_id': 200, 'event_type': 'view', 'product_id': 4, 'timestamp': 100200}
        ]
        for event in self.events:
            self.rs.update_event(event)

    def test_recommendations_not_empty(self):
        # Test that recommendations for a known user are returned as a non-empty list.
        recommendations = self.rs.get_recommendations(100, 3)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        for product_id in recommendations:
            self.assertIn(product_id, [1, 2, 3, 4])

    def test_cold_start_new_user(self):
        # Test that a new user with no history receives recommendations.
        recommendations = self.rs.get_recommendations(999, 2)
        self.assertEqual(len(recommendations), 2)
        for product_id in recommendations:
            self.assertIn(product_id, [1, 2, 3, 4])

    def test_recommendation_latency(self):
        # Test that recommendations are returned within 200ms.
        start_time = time.time()
        _ = self.rs.get_recommendations(100, 3)
        duration = (time.time() - start_time) * 1000  # convert to milliseconds
        self.assertLessEqual(duration, 200, msg=f"Recommendation took too long: {duration:.2f}ms")

    def test_algorithm_switching(self):
        # Test that switching algorithms updates the current algorithm and returns valid recommendations.
        initial_algo = self.rs.current_algorithm
        self.rs.switch_algorithm('collaborative_filtering')
        self.assertEqual(self.rs.current_algorithm, 'collaborative_filtering')
        self.rs.switch_algorithm('content_based')
        self.assertEqual(self.rs.current_algorithm, 'content_based')
        recommendations = self.rs.get_recommendations(100, 3)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_dynamic_catalog_update(self):
        # Test that updating the product catalog dynamically includes new products in recommendations.
        new_product = {'product_id': 5, 'category': 'books', 'price': 25.99, 'other_features': {'author': 'AuthorB'}}
        self.rs.update_catalog(new_product)
        recommendations = self.rs.get_recommendations(100, 5)
        self.assertIn(5, recommendations)

    def test_invalid_event_handling(self):
        # Test that a malformed event raises an exception.
        malformed_event = {'user_id': 300, 'event_type': 'invalid', 'timestamp': 100300}
        with self.assertRaises(Exception):
            self.rs.update_event(malformed_event)

    def test_performance_metrics_reporting(self):
        # Test that the performance metrics report includes required keys.
        metrics = self.rs.report_metrics()
        self.assertIn('hit_rate', metrics)
        self.assertIn('click_through_rate', metrics)
        self.assertIn('latency', metrics)

if __name__ == '__main__':
    unittest.main()