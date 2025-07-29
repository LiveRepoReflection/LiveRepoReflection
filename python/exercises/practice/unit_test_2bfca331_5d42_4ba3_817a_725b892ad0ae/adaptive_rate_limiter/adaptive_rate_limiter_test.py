import unittest
import time

from adaptive_rate_limiter import RateLimiter

class TestAdaptiveRateLimiter(unittest.TestCase):
    def setUp(self):
        # Initialize a new RateLimiter instance before each test
        self.limiter = RateLimiter()
        # Setup initial configuration for client1: 5 requests per 10 seconds
        self.limiter.update_client_config("client1", rate_limit=5, time_window=10)

    def test_allow_within_limit(self):
        # Within the limit, all requests should be allowed.
        start_time = 1000
        for i in range(5):
            response = self.limiter.process_request("client1", start_time + i)
            self.assertTrue(response['allowed'], f"Request {i+1} should be allowed")
            self.assertEqual(response['retry_after'], 0)

    def test_exceed_limit(self):
        # Exceed rate limit within the time window.
        start_time = 2000
        # Allow up to 5 requests.
        for i in range(5):
            response = self.limiter.process_request("client1", start_time)
            self.assertTrue(response['allowed'])
        
        # The 6th request should be rejected.
        response_exceed = self.limiter.process_request("client1", start_time)
        self.assertFalse(response_exceed['allowed'])
        self.assertGreater(response_exceed['retry_after'], 0)

    def test_reset_after_time_window(self):
        # After the time window passes, requests should be allowed again.
        start_time = 3000
        for i in range(5):
            response = self.limiter.process_request("client1", start_time)
            self.assertTrue(response['allowed'])
        
        # Simulate time passing beyond the time window.
        later_time = start_time + 11
        response_after = self.limiter.process_request("client1", later_time)
        self.assertTrue(response_after['allowed'])
        self.assertEqual(response_after['retry_after'], 0)

    def test_adaptive_throttling_reduction(self):
        # When backend response time is high, the effective rate limit should be reduced.
        # For client1 (configured limit: 5 per 10 sec), simulate high average response time.
        self.limiter.update_backend_response_time(600)  # Above the high threshold (e.g., 500ms)
        
        start_time = 4000
        allowed_count = 0
        # Assume the reduction factor brings the effective limit to 2 requests.
        for i in range(3):
            response = self.limiter.process_request("client1", start_time)
            if response['allowed']:
                allowed_count += 1
        self.assertEqual(allowed_count, 2, "With high backend response times, only 2 requests should be allowed")

    def test_adaptive_throttling_increase(self):
        # Test that after high response times, if backend recovers, effective limits increase.
        self.limiter.update_client_config("client1", rate_limit=6, time_window=10)
        self.limiter.update_backend_response_time(600)
        start_time = 5000
        # Use all available requests under high load.
        for i in range(6):
            self.limiter.process_request("client1", start_time)
        # Now simulate backend recovery: average response time falls (e.g., 150ms)
        self.limiter.update_backend_response_time(150)
        # Simulate the beginning of a new time window.
        later_time = start_time + 11
        allowed_count = 0
        for i in range(6):
            response = self.limiter.process_request("client1", later_time)
            if response['allowed']:
                allowed_count += 1
        # Expect the system to gradually restore up to the original rate limit.
        self.assertEqual(allowed_count, 6, "After backend recovery, effective limit should restore to configured maximum")

    def test_multiple_clients(self):
        # Verify that the limiter can handle multiple clients with different rate limits.
        self.limiter.update_client_config("client2", rate_limit=3, time_window=5)
        start_time = 6000

        # Test client1: 5 requests per 10 sec.
        for i in range(5):
            response = self.limiter.process_request("client1", start_time)
            self.assertTrue(response['allowed'])
        response_client1_extra = self.limiter.process_request("client1", start_time)
        self.assertFalse(response_client1_extra['allowed'])

        # Test client2: 3 requests per 5 sec.
        for i in range(3):
            response2 = self.limiter.process_request("client2", start_time)
            self.assertTrue(response2['allowed'])
        response_client2_extra = self.limiter.process_request("client2", start_time)
        self.assertFalse(response_client2_extra['allowed'])

    def test_retry_after_calculation(self):
        # Validate that the retry_after value is correctly calculated when a request is rate limited.
        start_time = 7000
        # Use client1 with a configuration of 5 requests per 10 seconds.
        for i in range(5):
            self.limiter.process_request("client1", start_time)
        # Make a rate limited request at time start_time + 2
        response = self.limiter.process_request("client1", start_time + 2)
        self.assertFalse(response['allowed'])
        # Since the first request was at 7000 and the time window is 10 sec,
        # retry_after should be about 10 - (2) = 8 seconds (allowing some delta for rounding).
        self.assertAlmostEqual(response['retry_after'], 8, delta=1)

if __name__ == '__main__':
    unittest.main()