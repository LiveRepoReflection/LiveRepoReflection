import unittest
import threading
import time
from distributed_counter.distributed_counter import DistributedCounter

class TestDistributedCounter(unittest.TestCase):
    def setUp(self):
        self.counter = DistributedCounter()

    def test_single_key_increment(self):
        self.counter.process_event("key1", 5)
        self.assertEqual(self.counter.get_count("key1"), 5)

    def test_key_does_not_exist(self):
        self.assertEqual(self.counter.get_count("nonexistent"), 0)

    def test_multiple_increments_same_key(self):
        self.counter.process_event("key1", 1)
        self.counter.process_event("key1", 2)
        self.counter.process_event("key1", 3)
        self.assertEqual(self.counter.get_count("key1"), 6)

    def test_negative_values(self):
        self.counter.process_event("key1", 10)
        self.counter.process_event("key1", -3)
        self.assertEqual(self.counter.get_count("key1"), 7)

    def test_multiple_keys(self):
        self.counter.process_event("key1", 1)
        self.counter.process_event("key2", 2)
        self.counter.process_event("key3", 3)
        self.assertEqual(self.counter.get_count("key1"), 1)
        self.assertEqual(self.counter.get_count("key2"), 2)
        self.assertEqual(self.counter.get_count("key3"), 3)

    def test_thread_safety(self):
        def worker():
            for _ in range(1000):
                self.counter.process_event("thread_key", 1)

        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(self.counter.get_count("thread_key"), 10000)

    def test_key_expiry(self):
        counter = DistributedCounter(expiry_seconds=1)
        counter.process_event("temp_key", 5)
        self.assertEqual(counter.get_count("temp_key"), 5)
        time.sleep(1.1)
        self.assertEqual(counter.get_count("temp_key"), 0)

    def test_persistence(self):
        self.counter.process_event("persistent_key", 42)
        self.counter._persist_counts()
        # In a real test, we would verify the persistence file here
        # This is just verifying the method exists and runs
        self.assertTrue(True)

    def test_large_number_of_keys(self):
        for i in range(10000):
            self.counter.process_event(f"key_{i}", i)
        self.assertEqual(self.counter.get_count("key_9999"), 9999)

    def test_mixed_operations(self):
        self.counter.process_event("mixed_key", 10)
        self.counter.process_event("mixed_key", -5)
        self.counter.process_event("mixed_key", 3)
        self.assertEqual(self.counter.get_count("mixed_key"), 8)

if __name__ == '__main__':
    unittest.main()