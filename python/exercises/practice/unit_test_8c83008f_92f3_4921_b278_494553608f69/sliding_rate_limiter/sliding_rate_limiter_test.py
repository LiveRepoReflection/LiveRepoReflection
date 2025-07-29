import unittest
import time
from sliding_rate_limiter import SlidingRateLimiter

class TestSlidingRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = SlidingRateLimiter()
        self.client_id = "test_client"
        self.limiter.update_limit(self.client_id, 5, 10)  # 5 requests per 10 seconds

    def test_single_request_allowed(self):
        self.assertTrue(self.limiter.is_allowed(self.client_id, int(time.time())))

    def test_max_requests_allowed(self):
        now = int(time.time())
        for _ in range(5):
            self.assertTrue(self.limiter.is_allowed(self.client_id, now))
    
    def test_request_over_limit_rejected(self):
        now = int(time.time())
        for _ in range(5):
            self.limiter.is_allowed(self.client_id, now)
        self.assertFalse(self.limiter.is_allowed(self.client_id, now))

    def test_sliding_window_behavior(self):
        now = int(time.time())
        # First 5 requests at time 0
        for _ in range(5):
            self.assertTrue(self.limiter.is_allowed(self.client_id, now))
        
        # After 9 seconds (still in window)
        self.assertFalse(self.limiter.is_allowed(self.client_id, now + 9))
        
        # After 11 seconds (window slides)
        self.assertTrue(self.limiter.is_allowed(self.client_id, now + 11))

    def test_multiple_clients(self):
        client2 = "client2"
        self.limiter.update_limit(client2, 2, 5)
        
        now = int(time.time())
        self.assertTrue(self.limiter.is_allowed(self.client_id, now))
        self.assertTrue(self.limiter.is_allowed(client2, now))
        
        for _ in range(4):
            self.limiter.is_allowed(self.client_id, now)
        
        self.assertFalse(self.limiter.is_allowed(self.client_id, now))
        self.assertTrue(self.limiter.is_allowed(client2, now))

    def test_limit_update(self):
        now = int(time.time())
        for _ in range(5):
            self.limiter.is_allowed(self.client_id, now)
        
        self.limiter.update_limit(self.client_id, 10, 10)
        self.assertTrue(self.limiter.is_allowed(self.client_id, now))

    def test_edge_case_empty_client(self):
        self.assertFalse(self.limiter.is_allowed("nonexistent_client", int(time.time())))

    def test_concurrent_requests(self):
        import threading
        
        results = []
        now = int(time.time())
        
        def make_request():
            results.append(self.limiter.is_allowed(self.client_id, now))
        
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(sum(results), 5)

if __name__ == '__main__':
    unittest.main()