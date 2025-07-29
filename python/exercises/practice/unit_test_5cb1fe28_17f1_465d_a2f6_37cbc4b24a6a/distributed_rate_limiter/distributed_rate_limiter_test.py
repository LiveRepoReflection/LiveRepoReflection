import unittest
import time
from unittest.mock import patch

from distributed_rate_limiter import allow_request

class FakeTime:
    def __init__(self, start):
        self.current = start
    def time(self):
        return self.current
    def sleep(self, seconds):
        self.current += seconds

class DistributedRateLimiterTest(unittest.TestCase):
    def test_allow_request_within_limit(self):
        fake_time = FakeTime(1000)
        with patch('distributed_rate_limiter.time.time', side_effect=fake_time.time):
            rate_limit = 3
            time_window = 10
            user_id = "user1"
            api_endpoint = "/api/test"
            # Allow up to rate_limit requests at the same moment
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))
            # Next request should be blocked as it exceeds the rate limit
            self.assertFalse(allow_request(user_id, api_endpoint, rate_limit, time_window))

    def test_allow_request_window_reset(self):
        fake_time = FakeTime(2000)
        with patch('distributed_rate_limiter.time.time', side_effect=fake_time.time):
            rate_limit = 2
            time_window = 5
            user_id = "user2"
            api_endpoint = "/api/data"
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))
            # The next request should be blocked within the same time window
            self.assertFalse(allow_request(user_id, api_endpoint, rate_limit, time_window))
            # Advance time beyond the window to reset the count
            fake_time.sleep(time_window + 1)
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))

    def test_allow_request_different_users_endpoints(self):
        fake_time = FakeTime(3000)
        with patch('distributed_rate_limiter.time.time', side_effect=fake_time.time):
            rate_limit = 3
            time_window = 10
            # Test for user1 and endpoint /api/one
            self.assertTrue(allow_request("user1", "/api/one", rate_limit, time_window))
            self.assertTrue(allow_request("user1", "/api/one", rate_limit, time_window))
            self.assertTrue(allow_request("user1", "/api/one", rate_limit, time_window))
            self.assertFalse(allow_request("user1", "/api/one", rate_limit, time_window))
            # Test for same user with a different endpoint should have independent count
            self.assertTrue(allow_request("user1", "/api/two", rate_limit, time_window))
            self.assertTrue(allow_request("user1", "/api/two", rate_limit, time_window))
            self.assertTrue(allow_request("user1", "/api/two", rate_limit, time_window))
            self.assertFalse(allow_request("user1", "/api/two", rate_limit, time_window))
            # Test for different user on the same endpoint
            self.assertTrue(allow_request("user2", "/api/one", rate_limit, time_window))
            self.assertTrue(allow_request("user2", "/api/one", rate_limit, time_window))
            self.assertTrue(allow_request("user2", "/api/one", rate_limit, time_window))
            self.assertFalse(allow_request("user2", "/api/one", rate_limit, time_window))

    def test_allow_request_edge_time_window(self):
        fake_time = FakeTime(4000)
        with patch('distributed_rate_limiter.time.time', side_effect=fake_time.time):
            rate_limit = 2
            time_window = 5
            user_id = "edge"
            api_endpoint = "/edge/test"
            # First request at time 4000
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))
            fake_time.sleep(2)  # time becomes 4002
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))
            # Next request should be blocked because rate limit reached within time_window
            self.assertFalse(allow_request(user_id, api_endpoint, rate_limit, time_window))
            fake_time.sleep(3)  # time becomes 4005, edge of or just beyond the window
            # Now, the first request (at t=4000) falls outside the current window, so a new request is allowed
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))

    def test_allow_request_concurrent_simulation(self):
        # Simulate an interleaved/concurrent sequence of requests.
        fake_time = FakeTime(5000)
        with patch('distributed_rate_limiter.time.time', side_effect=fake_time.time):
            rate_limit = 5
            time_window = 10
            user_id = "concurrent"
            api_endpoint = "/api/concurrent"
            results = []
            # Simulate 5 requests, one per second
            for _ in range(5):
                results.append(allow_request(user_id, api_endpoint, rate_limit, time_window))
                fake_time.sleep(1)
            self.assertEqual(results, [True, True, True, True, True])
            # A burst request immediately after should be blocked
            self.assertFalse(allow_request(user_id, api_endpoint, rate_limit, time_window))
            # After the time window, requests should be allowed again
            fake_time.sleep(time_window)
            self.assertTrue(allow_request(user_id, api_endpoint, rate_limit, time_window))

if __name__ == '__main__':
    unittest.main()