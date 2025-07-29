import unittest
from time import sleep
from threading import Thread
import random

class RateLimiterTest(unittest.TestCase):
    def setUp(self):
        try:
            from rate_limiter import RateLimiter
            self.RateLimiter = RateLimiter
        except ImportError:
            self.fail("Could not import RateLimiter class")

    def test_basic_rate_limiting(self):
        limiter = self.RateLimiter()
        client_id = "test_client"
        limiter.configure(client_id, requests=5, window_seconds=1)
        
        # Should allow 5 requests
        for _ in range(5):
            self.assertTrue(limiter.allow_request(client_id))
        
        # Should block the 6th request
        self.assertFalse(limiter.allow_request(client_id))
        
        # Wait for the window to reset
        sleep(1)
        
        # Should allow requests again
        self.assertTrue(limiter.allow_request(client_id))

    def test_multiple_clients(self):
        limiter = self.RateLimiter()
        client1 = "client1"
        client2 = "client2"
        
        limiter.configure(client1, requests=3, window_seconds=1)
        limiter.configure(client2, requests=2, window_seconds=1)
        
        # Test client1's limit
        self.assertTrue(limiter.allow_request(client1))
        self.assertTrue(limiter.allow_request(client1))
        self.assertTrue(limiter.allow_request(client1))
        self.assertFalse(limiter.allow_request(client1))
        
        # Test client2's limit (should be independent)
        self.assertTrue(limiter.allow_request(client2))
        self.assertTrue(limiter.allow_request(client2))
        self.assertFalse(limiter.allow_request(client2))

    def test_dynamic_rate_limit_update(self):
        limiter = self.RateLimiter()
        client_id = "dynamic_client"
        
        # Initial configuration
        limiter.configure(client_id, requests=2, window_seconds=1)
        
        self.assertTrue(limiter.allow_request(client_id))
        self.assertTrue(limiter.allow_request(client_id))
        self.assertFalse(limiter.allow_request(client_id))
        
        # Update configuration
        limiter.configure(client_id, requests=4, window_seconds=1)
        
        # Wait for window reset
        sleep(1)
        
        # Should now allow 4 requests
        self.assertTrue(limiter.allow_request(client_id))
        self.assertTrue(limiter.allow_request(client_id))
        self.assertTrue(limiter.allow_request(client_id))
        self.assertTrue(limiter.allow_request(client_id))
        self.assertFalse(limiter.allow_request(client_id))

    def test_concurrent_requests(self):
        limiter = self.RateLimiter()
        client_id = "concurrent_client"
        limiter.configure(client_id, requests=100, window_seconds=1)
        
        results = []
        
        def make_request():
            results.append(limiter.allow_request(client_id))
        
        # Create 150 concurrent requests
        threads = [Thread(target=make_request) for _ in range(150)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
        # Exactly 100 requests should have been allowed
        self.assertEqual(sum(1 for r in results if r), 100)
        self.assertEqual(sum(1 for r in results if not r), 50)

    def test_different_window_sizes(self):
        limiter = self.RateLimiter()
        client_id = "window_test_client"
        
        # Test with a very small window
        limiter.configure(client_id, requests=2, window_seconds=0.1)
        self.assertTrue(limiter.allow_request(client_id))
        self.assertTrue(limiter.allow_request(client_id))
        self.assertFalse(limiter.allow_request(client_id))
        
        sleep(0.1)  # Wait for small window to reset
        self.assertTrue(limiter.allow_request(client_id))

    def test_unconfigured_client(self):
        limiter = self.RateLimiter()
        with self.assertRaises(ValueError):
            limiter.allow_request("unknown_client")

    def test_invalid_configuration(self):
        limiter = self.RateLimiter()
        with self.assertRaises(ValueError):
            limiter.configure("client", requests=-1, window_seconds=1)
        with self.assertRaises(ValueError):
            limiter.configure("client", requests=1, window_seconds=0)

    def test_high_load(self):
        limiter = self.RateLimiter()
        num_clients = 100
        clients = [f"client_{i}" for i in range(num_clients)]
        
        # Configure different limits for each client
        for client in clients:
            limiter.configure(client, requests=random.randint(10, 50), window_seconds=1)
        
        # Make random requests
        for _ in range(1000):
            client = random.choice(clients)
            limiter.allow_request(client)  # Result doesn't matter, testing for errors
        
        # If we got here without errors, the test passes
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()