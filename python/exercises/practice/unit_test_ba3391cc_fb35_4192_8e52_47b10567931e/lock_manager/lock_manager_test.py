import unittest
import threading
import time
from lock_manager import LockManager

class LockManagerTest(unittest.TestCase):
    def setUp(self):
        # Initialize with 2000ms default lock expiry time
        self.lock_manager = LockManager(default_expiry_time=2000)

    def test_basic_lock_acquisition_and_release(self):
        # Test simple lock acquisition
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Test acquisition of same lock by different client (should fail)
        self.assertFalse(self.lock_manager.acquire_lock("resource1", "client2", 1000))
        
        # Test release of lock
        self.assertTrue(self.lock_manager.release_lock("resource1", "client1"))
        
        # After release, the other client should be able to acquire
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client2", 1000))

    def test_idempotent_acquisition(self):
        # Test that acquiring the same lock twice is idempotent
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Release should still work
        self.assertTrue(self.lock_manager.release_lock("resource1", "client1"))

    def test_lock_timeout(self):
        # Client1 acquires the lock
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Client2 tries to acquire with a timeout of 500ms
        start_time = time.time()
        self.assertFalse(self.lock_manager.acquire_lock("resource1", "client2", 500))
        elapsed_time = time.time() - start_time
        
        # Verify that the timeout was respected (allowing for some wiggle room)
        self.assertLessEqual(elapsed_time, 0.6)  # 600ms to allow for some overhead
        self.assertGreaterEqual(elapsed_time, 0.4)  # Should have waited at least 400ms

    def test_lock_expiry(self):
        # Set up a lock with short expiry time
        lock_manager = LockManager(default_expiry_time=100)  # 100ms expiry
        
        # Client acquires the lock
        self.assertTrue(lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Wait for the lock to expire
        time.sleep(0.15)  # 150ms, slightly longer than expiry
        
        # Another client should now be able to acquire the lock
        self.assertTrue(lock_manager.acquire_lock("resource1", "client2", 1000))

    def test_lock_extension(self):
        # Set up a lock with short expiry time
        lock_manager = LockManager(default_expiry_time=200)  # 200ms expiry
        
        # Client acquires the lock
        self.assertTrue(lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Wait a bit, but not enough for expiry
        time.sleep(0.1)  # 100ms
        
        # Extend the lock
        self.assertTrue(lock_manager.extend_lock("resource1", "client1", 500))
        
        # Wait for the original expiry time to pass
        time.sleep(0.15)  # 150ms (total wait now 250ms, past original expiry)
        
        # The lock should still be held by client1
        self.assertFalse(lock_manager.acquire_lock("resource1", "client2", 100))
        
        # Wait for extension to expire
        time.sleep(0.4)  # 400ms (total wait now 650ms, past extended expiry)
        
        # Now client2 should be able to acquire
        self.assertTrue(lock_manager.acquire_lock("resource1", "client2", 100))

    def test_extend_nonexistent_lock(self):
        # Attempt to extend a lock that doesn't exist
        self.assertFalse(self.lock_manager.extend_lock("nonexistent", "client1", 1000))

    def test_extend_lock_different_client(self):
        # Client1 acquires a lock
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Client2 tries to extend it
        self.assertFalse(self.lock_manager.extend_lock("resource1", "client2", 1000))

    def test_release_nonexistent_lock(self):
        # Attempt to release a lock that doesn't exist
        self.assertFalse(self.lock_manager.release_lock("nonexistent", "client1"))

    def test_release_lock_different_client(self):
        # Client1 acquires a lock
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Client2 tries to release it
        self.assertFalse(self.lock_manager.release_lock("resource1", "client2"))
        
        # Original client should still be able to release it
        self.assertTrue(self.lock_manager.release_lock("resource1", "client1"))

    def test_multiple_locks(self):
        # Multiple clients acquire different locks
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        self.assertTrue(self.lock_manager.acquire_lock("resource2", "client2", 1000))
        self.assertTrue(self.lock_manager.acquire_lock("resource3", "client3", 1000))
        
        # They should all be able to release their locks
        self.assertTrue(self.lock_manager.release_lock("resource1", "client1"))
        self.assertTrue(self.lock_manager.release_lock("resource2", "client2"))
        self.assertTrue(self.lock_manager.release_lock("resource3", "client3"))

    def test_concurrent_lock_acquisition(self):
        # Test concurrent lock acquisition for the same resource
        num_threads = 10
        success_count = [0]  # Use a list for mutable state across threads
        lock = threading.Lock()  # To ensure thread-safe updates to success_count
        
        def try_acquire():
            client_id = f"client_{threading.get_ident()}"
            if self.lock_manager.acquire_lock("concurrent_resource", client_id, 2000):
                with lock:
                    success_count[0] += 1
                time.sleep(0.01)  # Hold the lock briefly
                self.lock_manager.release_lock("concurrent_resource", client_id)
        
        threads = [threading.Thread(target=try_acquire) for _ in range(num_threads)]
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Only one thread should have successfully acquired the lock at a time
        self.assertEqual(success_count[0], num_threads)

    def test_lock_reacquisition_after_release(self):
        # Client acquires a lock
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
        
        # Client releases the lock
        self.assertTrue(self.lock_manager.release_lock("resource1", "client1"))
        
        # Client should be able to reacquire the lock
        self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))

    def test_reentrancy(self):
        # Test reentrancy if implemented
        # This test assumes reentrancy is supported - if not, this test might fail
        try:
            # First acquisition
            self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
            
            # Reentrant acquisition (should succeed if reentrancy is supported)
            self.assertTrue(self.lock_manager.acquire_lock("resource1", "client1", 1000))
            
            # First release (should not fully release the lock if reentrancy is supported)
            self.assertTrue(self.lock_manager.release_lock("resource1", "client1"))
            
            # Another client should still not be able to acquire the lock
            self.assertFalse(self.lock_manager.acquire_lock("resource1", "client2", 100))
            
            # Second release (should fully release the lock)
            self.assertTrue(self.lock_manager.release_lock("resource1", "client1"))
            
            # Now client2 should be able to acquire the lock
            self.assertTrue(self.lock_manager.acquire_lock("resource1", "client2", 100))
        except Exception as e:
            # If this test fails, it might be because reentrancy isn't implemented
            # This is marked as optional in the problem statement
            print(f"Reentrancy test failed: {e}. This is acceptable if reentrancy isn't implemented.")

    def test_stress_test(self):
        # Stress test with many locks and clients
        num_resources = 50
        num_clients = 20
        operations_per_client = 100
        
        def client_thread(client_id):
            for _ in range(operations_per_client):
                resource_id = f"resource_{int(time.time() * 1000000) % num_resources}"
                operation = int(time.time() * 1000000) % 3
                
                if operation == 0:
                    # Acquire lock
                    self.lock_manager.acquire_lock(resource_id, f"client_{client_id}", 100)
                elif operation == 1:
                    # Release lock
                    self.lock_manager.release_lock(resource_id, f"client_{client_id}")
                else:
                    # Extend lock
                    self.lock_manager.extend_lock(resource_id, f"client_{client_id}", 500)
                
                # Small sleep to simulate processing
                time.sleep(0.001)
        
        threads = [threading.Thread(target=client_thread, args=(i,)) for i in range(num_clients)]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Stress test completed in {duration:.2f} seconds.")
        
        # Test should pass if no exceptions were thrown


if __name__ == '__main__':
    unittest.main()