import unittest
import threading
import time

from dist_ratelimit import DistributedRateLimiter

class DistributedRateLimiterTestCase(unittest.TestCase):
    def setUp(self):
        # Set a low request limit and a short time window for testing.
        self.rate_limit = 5
        self.window_seconds = 1
        # Initialize a rate limiter instance. Assume it supports a distributed interface.
        self.limiter = DistributedRateLimiter(rate_limit=self.rate_limit, window_seconds=self.window_seconds)

    def test_single_client_within_limit(self):
        client_id = "client_single_within"
        # All requests should be allowed until the limit is reached.
        for i in range(self.rate_limit):
            allowed = self.limiter.allow_request(client_id)
            self.assertTrue(allowed, f"Request {i+1} for {client_id} should be allowed")
    
    def test_single_client_exceed_limit(self):
        client_id = "client_exceed"
        # Send requests reaching the limit.
        for i in range(self.rate_limit):
            allowed = self.limiter.allow_request(client_id)
            self.assertTrue(allowed, f"Request {i+1} for {client_id} should be allowed")
        # Next request should be rejected.
        allowed = self.limiter.allow_request(client_id)
        self.assertFalse(allowed, "Request exceeding the limit should be rejected")
    
    def test_reset_after_window(self):
        client_id = "client_reset"
        # Use all allowed requests.
        for i in range(self.rate_limit):
            self.assertTrue(self.limiter.allow_request(client_id), f"Request {i+1} for {client_id} should be allowed")
        # Exceed limit.
        self.assertFalse(self.limiter.allow_request(client_id), "Request exceeding the limit should be rejected")
        # Sleep until the time window resets.
        time.sleep(self.window_seconds + 0.1)
        # After window reset, requests should be allowed again.
        self.assertTrue(self.limiter.allow_request(client_id), "Request after window reset should be allowed")
    
    def test_multiple_clients(self):
        # Test multiple clients with independent rate limits.
        client_ids = [f"client_{i}" for i in range(10)]
        # Each client sends requests up to the limit.
        for client_id in client_ids:
            for j in range(self.rate_limit):
                self.assertTrue(self.limiter.allow_request(client_id),
                                f"Client {client_id} request {j+1} should be allowed")
            # Next request should be rejected.
            self.assertFalse(self.limiter.allow_request(client_id),
                             f"Client {client_id} request exceeding limit should be rejected")

    def test_concurrent_requests(self):
        # Test to mimic concurrent requests from the same client.
        client_id = "client_concurrent"
        results = []
        lock = threading.Lock()

        def send_request():
            allowed = self.limiter.allow_request(client_id)
            with lock:
                results.append(allowed)

        threads = []
        # Create more threads than the limit.
        for _ in range(self.rate_limit + 3):
            t = threading.Thread(target=send_request)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

        # Count true and false responses.
        allowed_count = results.count(True)
        rejected_count = results.count(False)
        self.assertEqual(allowed_count, self.rate_limit,
                         f"Exactly {self.rate_limit} requests should be allowed, got {allowed_count}")
        self.assertEqual(allowed_count + rejected_count, self.rate_limit + 3,
                         "Total request count mismatch in concurrent test")

    def test_distributed_consistency(self):
        # Simulate rate limiting calls from different "server" instances handling the same client.
        # Assume that each server creates its own instance of DistributedRateLimiter that
        # shares state through a distributed datastore.
        client_id = "client_distributed"
        limiter_instances = [DistributedRateLimiter(rate_limit=self.rate_limit, window_seconds=self.window_seconds)
                             for _ in range(3)]
        results = []

        def send_request(limiter):
            allowed = limiter.allow_request(client_id)
            results.append(allowed)

        threads = []
        # Create multiple threads from different limiter instances.
        for limiter in limiter_instances:
            for _ in range(3):
                t = threading.Thread(target=send_request, args=(limiter,))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        total_allowed = results.count(True)
        # Even distributed across multiple instances, the global allowed count should not exceed the rate limit.
        self.assertLessEqual(total_allowed, self.rate_limit,
                             f"Global allowed requests should not exceed {self.rate_limit}, got {total_allowed}")

if __name__ == '__main__':
    unittest.main()