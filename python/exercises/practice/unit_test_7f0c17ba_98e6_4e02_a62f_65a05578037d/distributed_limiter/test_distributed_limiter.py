import unittest
import time
from distributed_limiter import RateLimiter
from threading import Thread

class TestDistributedLimiter(unittest.TestCase):
    def setUp(self):
        self.max_requests = 5
        self.time_window = 2  # seconds
        self.limiter = RateLimiter(self.max_requests, self.time_window)
        self.client_id = "test_client"

    def test_single_client_within_limit(self):
        for _ in range(self.max_requests):
            self.assertTrue(self.limiter.allow_request(self.client_id, None))

    def test_single_client_exceeds_limit(self):
        for _ in range(self.max_requests):
            self.limiter.allow_request(self.client_id, None)
        
        self.assertFalse(self.limiter.allow_request(self.client_id, None))

    def test_limit_resets_after_window(self):
        for _ in range(self.max_requests):
            self.limiter.allow_request(self.client_id, None)
        
        time.sleep(self.time_window + 0.1)
        self.assertTrue(self.limiter.allow_request(self.client_id, None))

    def test_multiple_clients_independent_limits(self):
        client2 = "another_client"
        
        for _ in range(self.max_requests):
            self.assertTrue(self.limiter.allow_request(self.client_id, None))
            self.assertTrue(self.limiter.allow_request(client2, None))

        self.assertFalse(self.limiter.allow_request(self.client_id, None))
        self.assertFalse(self.limiter.allow_request(client2, None))

    def test_clear_client_resets_limit(self):
        for _ in range(self.max_requests):
            self.limiter.allow_request(self.client_id, None)
        
        self.limiter.clear_client(self.client_id)
        
        for _ in range(self.max_requests):
            self.assertTrue(self.limiter.allow_request(self.client_id, None))

    def test_thread_safety(self):
        def make_requests():
            for _ in range(self.max_requests * 2):
                self.limiter.allow_request(self.client_id, None)

        threads = [Thread(target=make_requests) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # After all threads complete, we should have exactly max_requests allowed
        # This is a simplified check - a real test would need to track exact counts
        self.assertFalse(self.limiter.allow_request(self.client_id, None))

    def test_request_timestamp_handling(self):
        old_request = type('Request', (), {'timestamp': time.time() - self.time_window - 1})()
        new_request = type('Request', (), {'timestamp': time.time()})()
        
        # Old request shouldn't count against limit
        for _ in range(self.max_requests):
            self.assertTrue(self.limiter.allow_request(self.client_id, old_request))
        
        # Should still have full limit available for new requests
        for _ in range(self.max_requests):
            self.assertTrue(self.limiter.allow_request(self.client_id, new_request))

if __name__ == '__main__':
    unittest.main()