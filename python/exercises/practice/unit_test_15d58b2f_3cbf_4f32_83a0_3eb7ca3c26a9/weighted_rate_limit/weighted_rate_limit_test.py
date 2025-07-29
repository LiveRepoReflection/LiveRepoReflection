import unittest
import threading

from weighted_rate_limit import WeightedRateLimiter

class WeightedRateLimiterTest(unittest.TestCase):
    def setUp(self):
        # Instantiate a fresh limiter for each test to ensure isolation
        self.limiter = WeightedRateLimiter()

    def test_single_request_allowed(self):
        # A single request should be allowed
        result = self.limiter.process_request("user1", "send_message", 1000, 1, 5, 1, "serverA")
        self.assertTrue(result)

    def test_exceeding_limit(self):
        # For a user with weight 1 and a limit of 3 actions per window,
        # the first 3 requests in the same time window should be allowed,
        # while the 4th should be rejected.
        ts = 1000
        results = []
        for _ in range(3):
            results.append(self.limiter.process_request("user1", "send_message", ts, 1, 3, 1, "serverA"))
        # Fourth request in same window should be rejected.
        results.append(self.limiter.process_request("user1", "send_message", ts, 1, 3, 1, "serverA"))
        self.assertTrue(all(results[:3]))
        self.assertFalse(results[3])

    def test_weighted_user(self):
        # For a user with weight=2 and base limit=3,
        # the allowed request count is multiplied by the weight (i.e., 6 actions allowed).
        ts = 2000
        results = []
        for _ in range(6):
            results.append(self.limiter.process_request("user2", "create_post", ts, 2, 3, 1, "serverB"))
        # Seventh request should be rejected.
        results.append(self.limiter.process_request("user2", "create_post", ts, 2, 3, 1, "serverB"))
        self.assertTrue(all(results[:6]))
        self.assertFalse(results[6])

    def test_time_window_reset(self):
        # Requests within a single time window should count towards the limit,
        # but once the window expires, new requests are allowed.
        ts = 3000
        # Fill the quota in current window.
        for _ in range(3):
            self.assertTrue(self.limiter.process_request("user3", "send_message", ts, 1, 3, 1, "serverA"))
        # Advance time beyond the window to reset limits.
        ts2 = ts + 2
        self.assertTrue(self.limiter.process_request("user3", "send_message", ts2, 1, 3, 1, "serverA"))

    def test_multiple_servers(self):
        # Requests arriving at different servers in the same window should aggregate the count.
        ts = 4000
        res1 = self.limiter.process_request("user4", "action", ts, 1, 3, 1, "serverA")
        res2 = self.limiter.process_request("user4", "action", ts, 1, 3, 1, "serverB")
        res3 = self.limiter.process_request("user4", "action", ts, 1, 3, 1, "serverC")
        res4 = self.limiter.process_request("user4", "action", ts, 1, 3, 1, "serverA")
        self.assertTrue(res1)
        self.assertTrue(res2)
        self.assertTrue(res3)
        self.assertFalse(res4)

    def test_concurrent_requests(self):
        # Simulate concurrent requests to test thread-safety of the rate limiter.
        ts = 5000
        user_id = "user_concurrent"
        total_requests = 10
        limit = 5
        weight = 1
        window = 1
        results = []
        
        def send_request():
            res = self.limiter.process_request(user_id, "send_message", ts, weight, limit, window, "serverA")
            results.append(res)
        
        threads = [threading.Thread(target=send_request) for _ in range(total_requests)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Only 'limit' number of requests should be allowed.
        self.assertEqual(results.count(True), limit)
        self.assertEqual(results.count(False), total_requests - limit)

if __name__ == '__main__':
    unittest.main()