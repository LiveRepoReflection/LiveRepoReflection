import unittest
from distributed_ratelimit import RateLimiter

class TestDistributedRateLimit(unittest.TestCase):
    def setUp(self):
        # Configuration: for each client, specify the maximum number of allowed requests
        # within a given time window (in seconds).
        config = {
            "client1": {"limit": 5, "window": 60},
            "client2": {"limit": 3, "window": 30},
        }
        self.rate_limiter = RateLimiter(config)

    def test_allow_under_limit(self):
        # Test that a client is allowed to make requests under the rate limit.
        request_time = 1000
        client_id = "client1"
        for i in range(5):
            request = {"client_id": client_id, "request_timestamp": request_time}
            response = self.rate_limiter.process(request)
            self.assertTrue(response["allowed"])
            expected_remaining = 5 - (i + 1)
            self.assertEqual(response["remaining_requests"], expected_remaining)
        # Next request should exceed the limit.
        request = {"client_id": client_id, "request_timestamp": request_time}
        response = self.rate_limiter.process(request)
        self.assertFalse(response["allowed"])
        self.assertIn("retry_after", response)
        self.assertGreater(response["retry_after"], 0)

    def test_rate_limit_reset_after_window(self):
        # After the time window expires, the client's allowance should reset.
        request_time = 2000
        client_id = "client1"
        for i in range(5):
            request = {"client_id": client_id, "request_timestamp": request_time}
            self.rate_limiter.process(request)
        # Exceed the limit within the same window.
        request = {"client_id": client_id, "request_timestamp": request_time}
        response = self.rate_limiter.process(request)
        self.assertFalse(response["allowed"])
        # Simulate a new time window.
        new_time = request_time + 61
        request = {"client_id": client_id, "request_timestamp": new_time}
        response = self.rate_limiter.process(request)
        self.assertTrue(response["allowed"])
        self.assertEqual(response["remaining_requests"], 4)

    def test_multiple_clients(self):
        # Verify that rate limits are enforced independently for different clients.
        t = 3000
        client1 = "client1"
        client2 = "client2"
        # First request for both clients.
        response1 = self.rate_limiter.process({"client_id": client1, "request_timestamp": t})
        self.assertTrue(response1["allowed"])
        response2 = self.rate_limiter.process({"client_id": client2, "request_timestamp": t})
        self.assertTrue(response2["allowed"])
        # Exhaust client2's limit.
        for _ in range(2):
            self.rate_limiter.process({"client_id": client2, "request_timestamp": t})
        response_exceed = self.rate_limiter.process({"client_id": client2, "request_timestamp": t})
        self.assertFalse(response_exceed["allowed"])
        self.assertIn("retry_after", response_exceed)
    
    def test_request_timestamps_edge(self):
        # Test requests that hit the boundaries of the time window.
        client_id = "client1"
        base_time = 4000
        # First request at the beginning.
        response = self.rate_limiter.process({"client_id": client_id, "request_timestamp": base_time})
        self.assertTrue(response["allowed"])
        # Make additional requests near the end of the window.
        request_time = base_time + 59
        for _ in range(4):
            r = self.rate_limiter.process({"client_id": client_id, "request_timestamp": request_time})
            self.assertTrue(r["allowed"])
        # This request should push over the limit.
        r = self.rate_limiter.process({"client_id": client_id, "request_timestamp": request_time})
        self.assertFalse(r["allowed"])
        self.assertIn("retry_after", r)
        # At the window boundary, the request should be allowed.
        r = self.rate_limiter.process({"client_id": client_id, "request_timestamp": base_time + 60})
        self.assertTrue(r["allowed"])
    
    def test_invalid_client(self):
        # Requests from an unknown client should be handled gracefully.
        # In this design, assume that an unknown client is not rate limited.
        request = {"client_id": "unknown_client", "request_timestamp": 5000}
        response = self.rate_limiter.process(request)
        self.assertTrue(response["allowed"])
        # When the client is unknown, remaining_requests is assumed to be unlimited.
        self.assertEqual(response["remaining_requests"], float("inf"))

if __name__ == "__main__":
    unittest.main()