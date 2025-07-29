import unittest
import time
from unittest.mock import patch, MagicMock

# Assume that the RecommendationEngine is implemented in the recommendation_optimization module.
from recommendation_optimization import RecommendationEngine

# Dummy service implementations to simulate microservices responses.
class DummyUserProfileService:
    def get_user_profile(self, user_id):
        return {"user_id": user_id, "preferences": ["electronics", "books"]}

class DummyProductCatalogService:
    def get_products(self):
        return [
            {"product_id": 1, "category": "electronics", "popularity": 90},
            {"product_id": 2, "category": "books", "popularity": 80},
            {"product_id": 3, "category": "clothing", "popularity": 70},
            {"product_id": 4, "category": "electronics", "popularity": 95},
        ]

class DummyOrderHistoryService:
    def get_order_history(self, user_id):
        return [{"order_id": 101, "items": [1, 2]}, {"order_id": 102, "items": [3]}]

class DummyInventoryService:
    def get_inventory(self, product_id):
        return {"product_id": product_id, "stock": 10}

class RecommendationEngineTest(unittest.TestCase):
    def setUp(self):
        # Initialize dummy services with simulated data.
        self.user_profile_service = DummyUserProfileService()
        self.product_catalog_service = DummyProductCatalogService()
        self.order_history_service = DummyOrderHistoryService()
        self.inventory_service = DummyInventoryService()
        
        # Create an instance of RecommendationEngine using dependency injection.
        # Assume the RecommendationEngine accepts services and caching options in its constructor.
        self.engine = RecommendationEngine(
            user_profile_service=self.user_profile_service,
            product_catalog_service=self.product_catalog_service,
            order_history_service=self.order_history_service,
            inventory_service=self.inventory_service,
            cache_enabled=True,
            cache_ttl=5  # seconds, short TTL for testing purposes
        )

    def test_generate_recommendations_normal(self):
        user_id = "user123"
        recommendations = self.engine.get_recommendations(user_id)
        # Verify that recommendations is a list and contains at least one recommendation.
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    @patch('recommendation_optimization.RecommendationEngine.fetch_order_history')
    def test_fallback_mechanism_order_history_failure(self, mock_fetch_order_history):
        # Simulate an exception when fetching order history.
        mock_fetch_order_history.side_effect = Exception("Order History Service Failure")
        user_id = "user123"
        recommendations = self.engine.get_recommendations(user_id)
        # Even if order history fails, the engine should still return recommendations (fallback behavior).
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_caching_mechanism(self):
        user_id = "user123"
        # First call should populate the cache.
        start_time = time.time()
        rec_first = self.engine.get_recommendations(user_id)
        first_duration = time.time() - start_time

        # Second call should be faster due to caching.
        start_time = time.time()
        rec_cached = self.engine.get_recommendations(user_id)
        second_duration = time.time() - start_time

        # Ensure that the recommendations are identical.
        self.assertEqual(rec_first, rec_cached)
        # Verify that the cached call is faster.
        self.assertGreater(first_duration, second_duration)

    def test_benchmark_latency(self):
        # Benchmark the recommendation generation over multiple iterations.
        iterations = 10
        latencies = []
        user_id = "user123"
        for _ in range(iterations):
            start_time = time.time()
            self.engine.get_recommendations(user_id)
            latencies.append(time.time() - start_time)
        average_latency = sum(latencies) / len(latencies)
        # The requirement specifies that average latency should be under 200ms.
        self.assertLess(average_latency, 0.2)

if __name__ == '__main__':
    unittest.main()