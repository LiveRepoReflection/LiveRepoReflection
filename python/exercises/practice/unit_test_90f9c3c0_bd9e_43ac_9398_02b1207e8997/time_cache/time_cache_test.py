import unittest
import threading
import time
from time_cache import TimeCache

class TestTimeCache(unittest.TestCase):
    def setUp(self):
        # Create a fresh instance of TimeCache for each test
        self.cache = TimeCache()

    def test_put_and_get_with_valid_ttl(self):
        # Test that a key is retrievable before TTL expires
        self.cache.put("key1", "value1", ttl=2)
        self.assertEqual(self.cache.get("key1"), "value1")
        # Wait less than ttl
        time.sleep(1)
        self.assertEqual(self.cache.get("key1"), "value1")
        # Wait until ttl expires
        time.sleep(1.5)
        self.assertIsNone(self.cache.get("key1"))

    def test_immediate_expiration_with_zero_and_negative_ttl(self):
        # Zero TTL should expire immediately
        self.cache.put("key_zero", "value_zero", ttl=0)
        self.assertIsNone(self.cache.get("key_zero"))
        # Negative TTL should expire immediately
        self.cache.put("key_negative", "value_negative", ttl=-5)
        self.assertIsNone(self.cache.get("key_negative"))

    def test_remove_key(self):
        self.cache.put("key2", "value2", ttl=5)
        # Remove should return True for existing key
        self.assertTrue(self.cache.remove("key2"))
        # After removal, get should return None
        self.assertIsNone(self.cache.get("key2"))
        # Removing non-existent key should return False
        self.assertFalse(self.cache.remove("key2"))

    def test_size_and_evict_expired(self):
        # Put multiple keys with different TTLs
        self.cache.put("key1", "value1", ttl=1)
        self.cache.put("key2", "value2", ttl=3)
        self.cache.put("key3", "value3", ttl=5)
        # Immediately, size should be 3.
        self.assertEqual(self.cache.size(), 3)
        # Wait until key1 expires
        time.sleep(1.2)
        # Before eviction, size still includes expired entries
        self.assertEqual(self.cache.size(), 3)
        # After eviction, key1 should be removed
        self.cache.evict_expired()
        self.assertEqual(self.cache.size(), 2)
        # key2 and key3 remain
        self.assertIsNone(self.cache.get("key1"))
        self.assertEqual(self.cache.get("key2"), "value2")
        self.assertEqual(self.cache.get("key3"), "value3")

    def test_concurrent_access(self):
        # Function for putting keys concurrently
        def put_entries(start, end):
            for i in range(start, end):
                self.cache.put(f"key{i}", f"value{i}", ttl=3)

        # Function for getting keys concurrently
        def get_entries(start, end, results):
            for i in range(start, end):
                results.append(self.cache.get(f"key{i}"))

        threads = []
        # Launch threads to put keys concurrently
        for i in range(3):
            t = threading.Thread(target=put_entries, args=(i*10, (i+1)*10))
            threads.append(t)
            t.start()

        # Wait for all put threads to finish
        for t in threads:
            t.join()

        # Verify all inserted keys are present
        for i in range(30):
            self.assertEqual(self.cache.get(f"key{i}"), f"value{i}")

        # Launch threads to concurrently remove some keys
        def remove_entries(start, end, removals):
            for i in range(start, end):
                if self.cache.remove(f"key{i}"):
                    removals.append(f"key{i}")

        removal_results = []
        remove_threads = []
        for i in range(3):
            t = threading.Thread(target=remove_entries, args=(i*5, (i+1)*5, removal_results))
            remove_threads.append(t)
            t.start()
        for t in remove_threads:
            t.join()

        # Check that removed keys are indeed gone
        for i in range(15):
            self.assertIsNone(self.cache.get(f"key{i}"))
        # And rest of the keys should still be available
        for i in range(15, 30):
            self.assertEqual(self.cache.get(f"key{i}"), f"value{i}")

    def test_eviction_of_multiple_expired_keys(self):
        # Insert keys with varying TTLs
        for i in range(5):
            # The first few keys expire quickly
            self.cache.put(f"fast_key_{i}", f"fast_value_{i}", ttl=1)
        for i in range(5):
            # Next keys have longer TTLs
            self.cache.put(f"slow_key_{i}", f"slow_value_{i}", ttl=4)
        self.assertEqual(self.cache.size(), 10)
        # Wait for fast keys to expire
        time.sleep(1.2)
        self.cache.evict_expired()
        self.assertEqual(self.cache.size(), 5)
        # Fast keys should be expired
        for i in range(5):
            self.assertIsNone(self.cache.get(f"fast_key_{i}"))
        # Slow keys should still be present
        for i in range(5):
            self.assertEqual(self.cache.get(f"slow_key_{i}"), f"slow_value_{i}")

if __name__ == "__main__":
    unittest.main()