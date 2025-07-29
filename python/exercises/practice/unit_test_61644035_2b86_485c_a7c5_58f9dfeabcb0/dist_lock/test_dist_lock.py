import unittest
import time
from threading import Thread
from queue import Queue

from dist_lock import DistributedLockService

class TestDistributedLockService(unittest.TestCase):
    def setUp(self):
        self.lock_service = DistributedLockService()

    def test_basic_lock_acquisition(self):
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        self.assertFalse(self.lock_service.acquire_lock("resource1", "client2", 1))
        self.lock_service.release_lock("resource1", "client1")
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client2", 1))

    def test_timeout(self):
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        start_time = time.time()
        self.assertFalse(self.lock_service.acquire_lock("resource1", "client2", 1))
        elapsed_time = time.time() - start_time
        self.assertLess(elapsed_time, 2)  # Should fail fast

    def test_heartbeat(self):
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        time.sleep(2)
        self.assertTrue(self.lock_service.heartbeat("resource1", "client1"))
        self.assertFalse(self.lock_service.acquire_lock("resource1", "client2", 1))

    def test_lease_expiration(self):
        self.lock_service = DistributedLockService(lease_duration=1)
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        time.sleep(2)  # Wait for lease to expire
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client2", 1))

    def test_concurrent_lock_acquisition(self):
        def worker(client_id, results):
            result = self.lock_service.acquire_lock("resource1", f"client{client_id}", 5)
            results.put((client_id, result))

        results = Queue()
        threads = []
        num_clients = 5

        for i in range(num_clients):
            thread = Thread(target=worker, args=(i, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Collect results
        success_count = 0
        while not results.empty():
            _, success = results.get()
            if success:
                success_count += 1

        self.assertEqual(success_count, 1)  # Only one client should succeed

    def test_idempotent_release(self):
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        self.assertTrue(self.lock_service.release_lock("resource1", "client1"))
        self.assertFalse(self.lock_service.release_lock("resource1", "client1"))

    def test_multiple_resources(self):
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        self.assertTrue(self.lock_service.acquire_lock("resource2", "client1", 5))
        self.assertFalse(self.lock_service.acquire_lock("resource1", "client2", 1))
        self.assertFalse(self.lock_service.acquire_lock("resource2", "client2", 1))

    def test_invalid_heartbeat(self):
        self.assertFalse(self.lock_service.heartbeat("resource1", "client1"))
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        self.assertTrue(self.lock_service.heartbeat("resource1", "client1"))
        self.assertFalse(self.lock_service.heartbeat("resource1", "client2"))

    def test_release_by_wrong_client(self):
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        self.assertFalse(self.lock_service.release_lock("resource1", "client2"))
        self.assertTrue(self.lock_service.release_lock("resource1", "client1"))

    def test_reacquire_after_release(self):
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))
        self.assertTrue(self.lock_service.release_lock("resource1", "client1"))
        self.assertTrue(self.lock_service.acquire_lock("resource1", "client1", 5))

if __name__ == '__main__':
    unittest.main()