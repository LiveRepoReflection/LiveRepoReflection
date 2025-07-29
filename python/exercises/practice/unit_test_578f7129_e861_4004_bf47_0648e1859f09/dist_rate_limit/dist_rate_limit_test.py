import unittest
import time
import threading

from dist_rate_limit import RateLimiter

class RateLimiterTestCase(unittest.TestCase):
    def setUp(self):
        # For testing purposes, set a small limit and window size.
        self.limit = 3  # Number of allowed requests per window
        self.window = 1  # Window size in seconds
        self.rl = RateLimiter(limit=self.limit, window=self.window)

    def test_single_user_under_limit(self):
        user = 'user1'
        current_time = time.time()
        # Allow exactly self.limit requests
        for _ in range(self.limit):
            allowed = self.rl.allow_request(user, current_time)
            self.assertTrue(allowed, "Request should be allowed when under the rate limit")
        # The next request in the same window should be rejected.
        allowed = self.rl.allow_request(user, current_time)
        self.assertFalse(allowed, "Request should be rejected when the limit is exceeded")

    def test_time_window_reset(self):
        user = 'user2'
        start = time.time()
        # Consume all allowed requests in the current window.
        for _ in range(self.limit):
            allowed = self.rl.allow_request(user, start)
            self.assertTrue(allowed)
        # Verify that additional requests in the same time window are rejected.
        self.assertFalse(self.rl.allow_request(user, start), "Request should be rejected in the same window")
        # Wait for the time window to pass.
        time.sleep(self.window + 0.1)
        # A new request after window expiration should be allowed.
        allowed = self.rl.allow_request(user, time.time())
        self.assertTrue(allowed, "Request should be allowed after the time window resets")

    def test_multiple_users(self):
        user1 = 'user1'
        user2 = 'user2'
        timestamp = time.time()
        # Both users should be allowed self.limit requests independently.
        for _ in range(self.limit):
            self.assertTrue(self.rl.allow_request(user1, timestamp))
            self.assertTrue(self.rl.allow_request(user2, timestamp))
        # Both users should receive a rejection once the limit is reached.
        self.assertFalse(self.rl.allow_request(user1, timestamp))
        self.assertFalse(self.rl.allow_request(user2, timestamp))

    def test_concurrent_requests(self):
        user = 'user_concurrent'
        results = []
        lock = threading.Lock()

        def make_request():
            allowed = self.rl.allow_request(user, time.time())
            with lock:
                results.append(allowed)

        threads = []
        # Launch more than self.limit threads to simulate concurrent requests.
        for _ in range(10):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        # Verify that only self.limit requests were allowed.
        allowed_count = sum(1 for allowed in results if allowed)
        self.assertEqual(allowed_count, self.limit, "Concurrent allowed requests should equal the configured rate limit")

    def test_non_increasing_timestamps(self):
        user = 'user_non_monotonic'
        base_time = time.time()
        # Simulate requests with non-monotonic timestamps.
        timestamps = [base_time, base_time - 0.5, base_time - 1.0]
        results = []
        for ts in timestamps:
            result = self.rl.allow_request(user, ts)
            results.append(result)
        # Ensure that the function returns boolean values without crashing.
        for result in results:
            self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main()