import unittest
import threading
import time
import random
import string

from obj_store import put, get

class TestObjectStore(unittest.TestCase):

    def generate_random_key(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def test_basic_put_get(self):
        key = "test_basic_put"
        data = b"hello world"
        put(key, data)
        retrieved = get(key)
        self.assertEqual(retrieved, data, "Basic put and get should return the stored data.")

    def test_non_existent_key(self):
        key = "non_existent_key"
        retrieved = get(key)
        self.assertIsNone(retrieved, "Getting a non-existent key should return None.")

    def test_large_data(self):
        key = "test_large_data"
        # create a large data blob of 2 MB (2*1024*1024 bytes)
        data = bytes([random.randint(0, 255) for _ in range(2 * 1024 * 1024)])
        put(key, data)
        retrieved = get(key)
        self.assertEqual(len(retrieved), len(data), "Retrieved large data should have the same size as the input.")
        self.assertEqual(retrieved, data, "Retrieved large data should match the stored data exactly.")

    def test_multiple_keys(self):
        keys = [f"key_{i}" for i in range(10)]
        data_items = [f"data_{i}".encode() for i in range(10)]
        for key, data in zip(keys, data_items):
            put(key, data)
        for key, data in zip(keys, data_items):
            retrieved = get(key)
            self.assertEqual(retrieved, data, f"Data for {key} should match the stored value.")

    def test_concurrent_puts_conflict_resolution(self):
        """
        Simulate concurrent updates to the same key to test conflict resolution.
        For the purpose of this test, we assume that the last write wins via vector clock comparison.
        """
        key = "concurrent_key"
        initial_data = b"init_data"
        put(key, initial_data)

        # Function for performing a put operation after a delay
        def perform_put(data, delay):
            time.sleep(delay)
            put(key, data)

        # Two concurrent puts with slight delays to simulate race conditions.
        thread1 = threading.Thread(target=perform_put, args=(b"version1", 0.1))
        thread2 = threading.Thread(target=perform_put, args=(b"version2", 0.2))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # After concurrent puts, get should return the data determined by the conflict resolution strategy.
        retrieved = get(key)
        # Since thread2 puts after thread1, we expect its version to be chosen as last-write-wins.
        self.assertEqual(retrieved, b"version2", "Conflict resolution should choose the last updated version.")

    def test_multiple_concurrent_puts(self):
        """
        Test concurrent puts from multiple threads with various delays.
        The expected outcome is that the value from the put with the maximum delay wins.
        """
        key = "multi_concurrent_key"
        versions = [f"ver_{i}".encode() for i in range(5)]
        delays = [random.uniform(0.01, 0.1) for _ in range(5)]

        threads = []
        for data, delay in zip(versions, delays):
            t = threading.Thread(target=lambda d, dl: put(key, d), args=(data, delay))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Knowing that the put operations occur concurrently,
        # we assume that the one with the longest delay is the last to be applied.
        # Find the version corresponding to the maximum delay.
        max_delay_index = delays.index(max(delays))
        expected = versions[max_delay_index]
        retrieved = get(key)
        self.assertEqual(retrieved, expected, "The version with the maximum delay (last write) should be returned.")

if __name__ == '__main__':
    unittest.main()