import unittest
import time
import threading
from rate_limit import RateLimiter

class TestRateLimiter(unittest.TestCase):
    def test_single_user_single_endpoint_within_limit(self):
        # Configure rate limit: allow 5 requests per 1 second
        limiter = RateLimiter(default_limit=5, window=1)
        # Send 5 requests and expect all to succeed.
        for _ in range(5):
            self.assertTrue(limiter.check_and_increment("user1", "endpoint1"))
        # The 6th request should be rejected.
        self.assertFalse(limiter.check_and_increment("user1", "endpoint1"))

    def test_single_user_single_endpoint_reset_after_window(self):
        # Configure rate limit: allow 3 requests per 1 second
        limiter = RateLimiter(default_limit=3, window=1)
        for _ in range(3):
            self.assertTrue(limiter.check_and_increment("user1", "endpoint1"))
        self.assertFalse(limiter.check_and_increment("user1", "endpoint1"))
        # Wait a bit longer than the window to allow reset.
        time.sleep(1.1)
        self.assertTrue(limiter.check_and_increment("user1", "endpoint1"))

    def test_multiple_users_and_endpoints(self):
        # Configure rate limit: allow 2 requests per 2 seconds per (user, endpoint).
        limiter = RateLimiter(default_limit=2, window=2)
        # Test on different combinations of user and endpoint.
        self.assertTrue(limiter.check_and_increment("user1", "endpoint1"))
        self.assertTrue(limiter.check_and_increment("user1", "endpoint2"))
        self.assertTrue(limiter.check_and_increment("user2", "endpoint1"))
        self.assertTrue(limiter.check_and_increment("user2", "endpoint2"))
        self.assertTrue(limiter.check_and_increment("user1", "endpoint1"))
        self.assertTrue(limiter.check_and_increment("user1", "endpoint2"))
        self.assertTrue(limiter.check_and_increment("user2", "endpoint1"))
        self.assertTrue(limiter.check_and_increment("user2", "endpoint2"))
        # Subsequent calls should be rejected.
        self.assertFalse(limiter.check_and_increment("user1", "endpoint1"))
        self.assertFalse(limiter.check_and_increment("user1", "endpoint2"))
        self.assertFalse(limiter.check_and_increment("user2", "endpoint1"))
        self.assertFalse(limiter.check_and_increment("user2", "endpoint2"))

    def test_concurrency_single_endpoint(self):
        # Configure rate limit: allow 50 requests per 2 seconds
        limiter = RateLimiter(default_limit=50, window=2)
        success_count = 0
        count_lock = threading.Lock()

        def worker():
            nonlocal success_count
            if limiter.check_and_increment("user1", "endpoint1"):
                with count_lock:
                    success_count += 1

        threads = []
        for _ in range(100):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        # Only 50 out of 100 concurrent calls should succeed.
        self.assertEqual(success_count, 50)

    def test_concurrent_multiple_users(self):
        # Configure rate limit: allow 30 requests per 2 seconds per (user, endpoint)
        limiter = RateLimiter(default_limit=30, window=2)
        results = {}
        results_lock = threading.Lock()

        def worker(user, endpoint):
            if limiter.check_and_increment(user, endpoint):
                with results_lock:
                    results.setdefault((user, endpoint), 0)
                    results[(user, endpoint)] += 1

        threads = []
        users = ["u1", "u2", "u3"]
        endpoints = ["e1", "e2"]
        for user in users:
            for endpoint in endpoints:
                for _ in range(40):  # 40 attempts per user-endpoint pair, limit is 30
                    t = threading.Thread(target=worker, args=(user, endpoint))
                    threads.append(t)
                    t.start()
        for t in threads:
            t.join()

        # For each (user, endpoint) pair, exactly 30 requests should succeed.
        for user in users:
            for endpoint in endpoints:
                self.assertEqual(results.get((user, endpoint), 0), 30)

if __name__ == '__main__':
    unittest.main()