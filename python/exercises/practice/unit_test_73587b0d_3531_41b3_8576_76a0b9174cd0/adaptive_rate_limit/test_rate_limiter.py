import unittest
import threading
import time
from adaptive_rate_limit.rate_limiter import RateLimiter

class TestBasicRateLimit(unittest.TestCase):
    def setUp(self):
        # Create a new RateLimiter instance.
        # Assume the constructor sets up a distributed store connection.
        self.limiter = RateLimiter()
        # Configure user 'user1' for 5 requests per minute.
        self.user_id = 'user1'
        self.rate_limit = 5
        self.window = 60
        self.limiter.set_user_rate_limit(self.user_id, self.rate_limit, self.window)

    def test_requests_within_limit(self):
        # Light load conditions.
        current_server_load = 0.1
        network_latency = 20  # ms
        base_timestamp = int(time.time())

        # Allow up to rate_limit requests.
        allowed = 0
        for i in range(self.rate_limit):
            ts = base_timestamp + i
            if self.limiter.check_request(self.user_id, ts, current_server_load, network_latency):
                allowed += 1
        self.assertEqual(allowed, self.rate_limit)

    def test_exceeding_rate_limit(self):
        current_server_load = 0.1
        network_latency = 20  # ms
        base_timestamp = int(time.time())

        # Exceed the limit.
        results = []
        for i in range(self.rate_limit + 2):
            ts = base_timestamp + i
            results.append(self.limiter.check_request(self.user_id, ts, current_server_load, network_latency))
        # Ensure that at least one request beyond the limit is rejected.
        self.assertTrue(results.count(True) <= self.rate_limit)
        self.assertTrue(False in results)

class TestAdaptiveThrottling(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()
        # Configure user 'user2' for 6 requests per minute.
        self.user_id = 'user2'
        self.rate_limit = 6
        self.window = 60
        self.limiter.set_user_rate_limit(self.user_id, self.rate_limit, self.window)

    def test_adaptive_throttling_under_high_load(self):
        # Under high load and high latency, assume effective limit is reduced.
        high_load = 0.95
        high_latency = 500  # ms
        base_timestamp = int(time.time())

        allowed = 0
        results = []
        # We attempt more requests than the normal limit.
        for i in range(self.rate_limit + 3):
            ts = base_timestamp + i
            allowed_request = self.limiter.check_request(self.user_id, ts, high_load, high_latency)
            results.append(allowed_request)
            if allowed_request:
                allowed += 1

        # Under heavy load, we want to see that fewer requests are allowed than the configured rate.
        self.assertTrue(allowed < self.rate_limit)
        self.assertTrue(False in results)

class TestDynamicConfiguration(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()
        self.user_id = 'user3'
        # Start with a low rate limit.
        self.initial_limit = 3
        self.window = 60
        self.limiter.set_user_rate_limit(self.user_id, self.initial_limit, self.window)

    def test_dynamic_rate_limit_update(self):
        current_server_load = 0.1
        network_latency = 20  # ms
        base_timestamp = int(time.time())

        allowed_initial = 0
        for i in range(self.initial_limit):
            ts = base_timestamp + i
            if self.limiter.check_request(self.user_id, ts, current_server_load, network_latency):
                allowed_initial += 1
        self.assertEqual(allowed_initial, self.initial_limit)

        # Update the rate limit for user3 to a higher value.
        new_limit = 5
        self.limiter.set_user_rate_limit(self.user_id, new_limit, self.window)
        allowed_new = 0
        # Start a fresh window.
        new_base_timestamp = base_timestamp + self.window + 1
        for i in range(new_limit):
            ts = new_base_timestamp + i
            if self.limiter.check_request(self.user_id, ts, current_server_load, network_latency):
                allowed_new += 1
        self.assertEqual(allowed_new, new_limit)

class TestConcurrentRequests(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()
        self.user_id = 'user4'
        self.rate_limit = 10
        self.window = 60
        self.limiter.set_user_rate_limit(self.user_id, self.rate_limit, self.window)

    def worker(self, results, idx, base_timestamp, current_server_load, network_latency):
        ts = base_timestamp + idx
        result = self.limiter.check_request(self.user_id, ts, current_server_load, network_latency)
        results[idx] = result

    def test_concurrent_access(self):
        thread_count = 20  # More threads than the rate limit.
        threads = []
        results = [None] * thread_count
        base_timestamp = int(time.time())
        current_server_load = 0.1
        network_latency = 20  # ms

        for i in range(thread_count):
            thread = threading.Thread(target=self.worker, args=(results, i, base_timestamp, current_server_load, network_latency))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        allowed_count = results.count(True)
        self.assertTrue(allowed_count <= self.rate_limit)

if __name__ == '__main__':
    unittest.main()