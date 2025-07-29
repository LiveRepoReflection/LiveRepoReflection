import unittest
import time
import threading
import random
from unittest.mock import MagicMock, patch
from adaptive_limiter import DistributedRateLimiter, AdaptiveThresholder, SystemMetrics


class MockRedis:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def incr(self, key):
        with self.lock:
            if key not in self.data:
                self.data[key] = 0
            self.data[key] += 1
            return self.data[key]

    def get(self, key):
        with self.lock:
            return self.data.get(key, 0)
            
    def set(self, key, value, ex=None):
        with self.lock:
            self.data[key] = value
            
    def expire(self, key, seconds):
        pass  # Mock implementation doesn't handle expirations
        
    def ttl(self, key):
        return 60  # Default ttl for tests


class TestSystemMetrics(unittest.TestCase):
    
    def test_get_cpu_utilization(self):
        metrics = SystemMetrics()
        # Mock external CPU measurements
        with patch.object(metrics, '_get_cpu_utilization_from_system', return_value=0.75):
            self.assertEqual(metrics.get_cpu_utilization(), 0.75)
            
    def test_get_request_latency(self):
        metrics = SystemMetrics()
        # Mock latency measurements
        with patch.object(metrics, '_get_request_latency_from_system', return_value=150):
            self.assertEqual(metrics.get_request_latency(), 150)
            
    def test_get_error_rate(self):
        metrics = SystemMetrics()
        # Mock error rate measurements
        with patch.object(metrics, '_get_error_rate_from_system', return_value=0.05):
            self.assertEqual(metrics.get_error_rate(), 0.05)
            
    def test_update_metrics(self):
        metrics = SystemMetrics()
        # Mock all metric sources
        with patch.object(metrics, '_get_cpu_utilization_from_system', return_value=0.8), \
             patch.object(metrics, '_get_request_latency_from_system', return_value=200), \
             patch.object(metrics, '_get_error_rate_from_system', return_value=0.1):
            
            metrics.update_metrics()
            self.assertEqual(metrics.get_cpu_utilization(), 0.8)
            self.assertEqual(metrics.get_request_latency(), 200)
            self.assertEqual(metrics.get_error_rate(), 0.1)


class TestAdaptiveThresholder(unittest.TestCase):
    
    def setUp(self):
        self.metrics = SystemMetrics()
        self.mock_metrics = {
            'cpu_utilization': 0.5,
            'request_latency': 100,
            'error_rate': 0.02
        }
        
        # Mock the metrics
        self.metrics.get_cpu_utilization = MagicMock(return_value=self.mock_metrics['cpu_utilization'])
        self.metrics.get_request_latency = MagicMock(return_value=self.mock_metrics['request_latency'])
        self.metrics.get_error_rate = MagicMock(return_value=self.mock_metrics['error_rate'])
        
        self.thresholder = AdaptiveThresholder(
            base_limit=100,
            metrics=self.metrics,
            cpu_weight=0.4,
            latency_weight=0.4,
            error_weight=0.2,
            update_interval=1
        )
        
    def test_calculate_adaptive_limit(self):
        limit = self.thresholder.calculate_adaptive_limit()
        self.assertGreater(limit, 0)
        
        # Test with higher CPU utilization (should reduce limit)
        self.metrics.get_cpu_utilization = MagicMock(return_value=0.9)
        high_cpu_limit = self.thresholder.calculate_adaptive_limit()
        self.assertLess(high_cpu_limit, limit)
        
        # Test with increased error rate (should reduce limit)
        self.metrics.get_cpu_utilization = MagicMock(return_value=0.5)  # Reset CPU
        self.metrics.get_error_rate = MagicMock(return_value=0.1)
        high_error_limit = self.thresholder.calculate_adaptive_limit()
        self.assertLess(high_error_limit, limit)
        
    def test_update_thread(self):
        self.thresholder.start()
        time.sleep(1.5)  # Allow time for at least one update
        
        # Check if the limit was updated
        self.assertNotEqual(self.thresholder.current_limit, 0)
        
        self.thresholder.stop()
        

class TestDistributedRateLimiter(unittest.TestCase):
    
    def setUp(self):
        self.redis_client = MockRedis()
        
        # Create a mock thresholder with predictable limit
        self.mock_thresholder = MagicMock()
        self.mock_thresholder.calculate_adaptive_limit = MagicMock(return_value=100)
        self.mock_thresholder.get_current_limit = MagicMock(return_value=100)
        
        self.limiter = DistributedRateLimiter(
            redis_client=self.redis_client,
            thresholder=self.mock_thresholder,
            window_size=60  # 60 second window
        )
        
    def test_check_rate_limit_global(self):
        # Should allow first 100 requests
        for i in range(100):
            result = self.limiter.check_rate_limit()
            self.assertTrue(result.allowed)
            self.assertEqual(result.limit, 100)
            self.assertEqual(result.remaining, 100 - (i + 1))
            
        # 101st request should be blocked
        result = self.limiter.check_rate_limit()
        self.assertFalse(result.allowed)
        self.assertEqual(result.limit, 100)
        self.assertEqual(result.remaining, 0)
        
    def test_check_rate_limit_user(self):
        user_id = "test_user"
        
        # Should allow first 100 requests for this user
        for i in range(100):
            result = self.limiter.check_rate_limit(user_id=user_id)
            self.assertTrue(result.allowed)
            
        # 101st request should be blocked for this user
        result = self.limiter.check_rate_limit(user_id=user_id)
        self.assertFalse(result.allowed)
        
        # But other users should still be allowed
        result = self.limiter.check_rate_limit(user_id="other_user")
        self.assertTrue(result.allowed)
        
    def test_check_rate_limit_endpoint(self):
        endpoint = "/api/resource"
        
        # Should allow first 100 requests to this endpoint
        for i in range(100):
            result = self.limiter.check_rate_limit(endpoint=endpoint)
            self.assertTrue(result.allowed)
            
        # 101st request should be blocked for this endpoint
        result = self.limiter.check_rate_limit(endpoint=endpoint)
        self.assertFalse(result.allowed)
        
        # But other endpoints should still be allowed
        result = self.limiter.check_rate_limit(endpoint="/api/other")
        self.assertTrue(result.allowed)
        
    def test_check_rate_limit_combined(self):
        user_id = "test_user"
        endpoint = "/api/resource"
        
        # Should allow first 100 requests for this user+endpoint combination
        for i in range(100):
            result = self.limiter.check_rate_limit(user_id=user_id, endpoint=endpoint)
            self.assertTrue(result.allowed)
            
        # 101st request should be blocked for this combination
        result = self.limiter.check_rate_limit(user_id=user_id, endpoint=endpoint)
        self.assertFalse(result.allowed)
        
        # But same user with different endpoint should still be allowed
        result = self.limiter.check_rate_limit(user_id=user_id, endpoint="/api/other")
        self.assertTrue(result.allowed)
        
        # And different user with same endpoint should still be allowed
        result = self.limiter.check_rate_limit(user_id="other_user", endpoint=endpoint)
        self.assertTrue(result.allowed)

    def test_adaptive_limits(self):
        # Test with changing limits
        self.mock_thresholder.get_current_limit = MagicMock(return_value=50)
        
        # Should allow only 50 requests now
        for i in range(50):
            result = self.limiter.check_rate_limit()
            self.assertTrue(result.allowed)
            
        # 51st request should be blocked
        result = self.limiter.check_rate_limit()
        self.assertFalse(result.allowed)
        
        # Now increase the limit
        self.mock_thresholder.get_current_limit = MagicMock(return_value=150)
        
        # Should allow more requests
        result = self.limiter.check_rate_limit()
        self.assertTrue(result.allowed)

    def test_concurrent_requests(self):
        num_threads = 20
        requests_per_thread = 10
        
        self.mock_thresholder.get_current_limit = MagicMock(return_value=150)
        
        def make_requests():
            results = []
            for _ in range(requests_per_thread):
                results.append(self.limiter.check_rate_limit().allowed)
            return results
            
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=make_requests)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # Verify the total number of requests
        count = self.redis_client.get('ratelimit:global:counter')
        self.assertEqual(count, num_threads * requests_per_thread)
        
        # Check that we hit the limit
        result = self.limiter.check_rate_limit()
        self.assertFalse(result.allowed)


if __name__ == '__main__':
    unittest.main()