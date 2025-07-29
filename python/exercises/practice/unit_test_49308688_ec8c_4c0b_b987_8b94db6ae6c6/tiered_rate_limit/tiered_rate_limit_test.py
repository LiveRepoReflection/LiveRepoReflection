import unittest
from unittest.mock import patch, MagicMock
import time

# Assume the implementation of is_request_allowed is in tiered_rate_limit.py
from tiered_rate_limit import is_request_allowed

class TieredRateLimitTest(unittest.TestCase):
    def setUp(self):
        # A simple store to simulate client counters for each minute window.
        # This is only used for simulating consistent timestamp increments.
        self.initial_timestamp = 1000

    @patch("tiered_rate_limit.log_request")
    @patch("tiered_rate_limit.get_rate_limit")
    @patch("tiered_rate_limit.get_client_tier")
    def test_free_tier_limit(self, mock_get_client_tier, mock_get_rate_limit, mock_log_request):
        # Setup for Free tier, limit = 10 requests per minute
        client_id = "client_free_1"
        mock_get_client_tier.return_value = "Free"
        mock_get_rate_limit.return_value = 10

        # Allow exactly 10 requests in the same time window, 11th should be blocked.
        allowed_results = []
        for i in range(10):
            result = is_request_allowed(client_id, self.initial_timestamp)
            allowed_results.append(result)
        # 11th request in the same window should be disallowed
        result_11 = is_request_allowed(client_id, self.initial_timestamp)
        
        self.assertTrue(all(allowed_results), "First 10 free-tier requests should be allowed")
        self.assertFalse(result_11, "11th free-tier request should be rate limited")

    @patch("tiered_rate_limit.log_request")
    @patch("tiered_rate_limit.get_rate_limit")
    @patch("tiered_rate_limit.get_client_tier")
    def test_time_window_reset(self, mock_get_client_tier, mock_get_rate_limit, mock_log_request):
        # Setup for Free tier, limit = 10 requests per minute
        client_id = "client_free_2"
        mock_get_client_tier.return_value = "Free"
        mock_get_rate_limit.return_value = 10

        # Simulate 10 requests at time T (allowed)
        for _ in range(10):
            allowed = is_request_allowed(client_id, self.initial_timestamp)
            self.assertTrue(allowed, "Request should be allowed within the first window")
        
        # 11th request in the same minute should be blocked
        self.assertFalse(is_request_allowed(client_id, self.initial_timestamp), "Request exceeding limit should be blocked")
        
        # Advance time by 61 seconds to simulate a new window. Requests should be allowed again.
        new_timestamp = self.initial_timestamp + 61
        allowed_new_window = is_request_allowed(client_id, new_timestamp)
        self.assertTrue(allowed_new_window, "Request should be allowed in a new time window")

    @patch("tiered_rate_limit.log_request")
    @patch("tiered_rate_limit.get_rate_limit")
    @patch("tiered_rate_limit.get_client_tier")
    def test_multiple_tiers(self, mock_get_client_tier, mock_get_rate_limit, mock_log_request):
        # Setup different return values based on client_id
        def mock_get_client_tier_side_effect(client_id):
            if "free" in client_id:
                return "Free"
            elif "basic" in client_id:
                return "Basic"
            elif "premium" in client_id:
                return "Premium"
            return "Free"
        
        def mock_get_rate_limit_side_effect(tier):
            if tier == "Free":
                return 10
            elif tier == "Basic":
                return 100
            elif tier == "Premium":
                return 1000
            return 10

        mock_get_client_tier.side_effect = mock_get_client_tier_side_effect
        mock_get_rate_limit.side_effect = mock_get_rate_limit_side_effect

        # For free tier client, simulate reaching the limit.
        free_client = "client_free_3"
        for i in range(10):
            self.assertTrue(is_request_allowed(free_client, self.initial_timestamp), f"Free tier request {i+1} should be allowed")
        self.assertFalse(is_request_allowed(free_client, self.initial_timestamp), "Free tier exceeding request should be blocked")

        # For basic tier client, simulate 50 requests which should all be allowed.
        basic_client = "client_basic_1"
        for i in range(50):
            self.assertTrue(is_request_allowed(basic_client, self.initial_timestamp), f"Basic tier request {i+1} should be allowed")
        
        # For premium tier client, simulate 500 requests which should all be allowed.
        premium_client = "client_premium_1"
        for i in range(500):
            self.assertTrue(is_request_allowed(premium_client, self.initial_timestamp), f"Premium tier request {i+1} should be allowed")
        
    @patch("tiered_rate_limit.log_request")
    @patch("tiered_rate_limit.get_rate_limit")
    @patch("tiered_rate_limit.get_client_tier")
    def test_separate_clients(self, mock_get_client_tier, mock_get_rate_limit, mock_log_request):
        # Ensure multiple clients maintain independent rate limits.
        def mock_get_client_tier_side_effect(client_id):
            # Alternate tiers for testing
            if client_id.startswith("free"):
                return "Free"
            return "Basic"
        
        def mock_get_rate_limit_side_effect(tier):
            if tier == "Free":
                return 10
            if tier == "Basic":
                return 100
            return 10

        mock_get_client_tier.side_effect = mock_get_client_tier_side_effect
        mock_get_rate_limit.side_effect = mock_get_rate_limit_side_effect

        client_free = "free_client_1"
        client_basic = "basic_client_1"
        
        # Send 10 requests for free client, then 1 extra.
        for i in range(10):
            self.assertTrue(is_request_allowed(client_free, self.initial_timestamp), f"Free client request {i+1} should be allowed")
        self.assertFalse(is_request_allowed(client_free, self.initial_timestamp), "Free client exceeding request should be blocked")

        # Basic client should still be allowed for up to 100 requests.
        for i in range(100):
            self.assertTrue(is_request_allowed(client_basic, self.initial_timestamp), f"Basic client request {i+1} should be allowed")
        self.assertFalse(is_request_allowed(client_basic, self.initial_timestamp), "Basic client exceeding request should be blocked")
    
    @patch("tiered_rate_limit.log_request")
    @patch("tiered_rate_limit.get_rate_limit")
    @patch("tiered_rate_limit.get_client_tier")
    def test_logging_called(self, mock_get_client_tier, mock_get_rate_limit, mock_log_request):
        # Verify that log_request is called for each request processed.
        client_id = "client_logging_test"
        mock_get_client_tier.return_value = "Free"
        mock_get_rate_limit.return_value = 5

        # Execute 7 requests, with the first 5 allowed and next 2 blocked.
        results = []
        for _ in range(7):
            results.append(is_request_allowed(client_id, self.initial_timestamp))
        
        self.assertEqual(len(results), 7, "All requests should return a boolean result")
        # Verify that log_request is called 7 times
        self.assertEqual(mock_log_request.call_count, 7, "log_request should be called for every request processed")
        
if __name__ == "__main__":
    unittest.main()