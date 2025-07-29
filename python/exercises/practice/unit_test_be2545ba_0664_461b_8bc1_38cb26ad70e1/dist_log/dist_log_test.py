import unittest
import threading
import time

# We assume that the implementation of DistLog is provided in the dist_log module.
from dist_log import DistLog

class DistLogTest(unittest.TestCase):
    def setUp(self):
        # Create a new instance of the distributed log before each test.
        # It is assumed that DistLog resets its internal state on instantiation.
        self.log = DistLog()

    def test_append_returns_valid_indices(self):
        # Test that appending entries returns the correct monotonically increasing index.
        first_index = self.log.append("first entry")
        self.assertEqual(first_index, 1)
        second_index = self.log.append("second entry")
        self.assertEqual(second_index, 2)
        third_index = self.log.append("third entry")
        self.assertEqual(third_index, 3)

    def test_read_valid_data(self):
        # Append some data and check if the read function returns the correct data.
        index1 = self.log.append("entry one")
        index2 = self.log.append("entry two")
        # Read back the entries
        self.assertEqual(self.log.read(index1), "entry one")
        self.assertEqual(self.log.read(index2), "entry two")

    def test_get_highest_index(self):
        # Check get_highest_index functionality.
        self.assertEqual(self.log.get_highest_index(), 0)
        self.log.append("entry one")
        self.assertEqual(self.log.get_highest_index(), 1)
        self.log.append("entry two")
        self.assertEqual(self.log.get_highest_index(), 2)

    def test_invalid_read_index(self):
        # Test that reading an index less than 1 raises an exception.
        with self.assertRaises(ValueError):
            self.log.read(0)

        # Also test reading a non-existent index (greater than highest_index) should block.
        # We'll run this in a thread and then cancel the wait by adding the entry.
        def read_invalid():
            return self.log.read(5)

        read_thread = threading.Thread(target=read_invalid)
        read_thread.daemon = True
        read_thread.start()
        # Sleep briefly to ensure the read is blocking.
        time.sleep(0.5)
        # Now append entries until index 5 is reached.
        for _ in range(5 - self.log.get_highest_index()):
            self.log.append("filler entry")
        # Wait for thread to complete (should complete after the append)
        read_thread.join(timeout=2)
        self.assertFalse(read_thread.is_alive(), "The blocking read did not finish as expected.")

    def test_blocking_read_behavior(self):
        # Test that a read call that is waiting for an index correctly unblocks when the entry is appended.
        result_container = []

        def blocking_read():
            try:
                value = self.log.read(2)
                result_container.append(value)
            except Exception as e:
                result_container.append(e)

        read_thread = threading.Thread(target=blocking_read)
        read_thread.start()
        # Ensure thread is waiting by sleeping a moment.
        time.sleep(0.5)
        # Append a single entry (still not enough to satisfy read(2))
        self.log.append("first entry")
        # Wait a moment to be sure read is still blocked
        time.sleep(0.5)
        self.assertEqual(len(result_container), 0, "Read unblocked too early.")
        # Append the second entry to unblock the read.
        self.log.append("second entry")
        # Wait for thread to complete.
        read_thread.join(timeout=2)
        self.assertFalse(read_thread.is_alive(), "The blocking read did not finish after appending the required entry.")
        self.assertEqual(result_container[0], "second entry")

    def test_concurrent_appends(self):
        # Test appending concurrently from multiple threads.
        append_count = 50
        results = []
        lock = threading.Lock()

        def append_entries():
            for i in range(append_count):
                idx = self.log.append(f"entry {i}")
                with lock:
                    results.append(idx)
                # Simulate a small delay
                time.sleep(0.01)

        threads = [threading.Thread(target=append_entries) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Check that indexes are unique and monotonically increasing from 1 to total number of appends.
        total_appends = 3 * append_count
        self.assertEqual(sorted(results), list(range(1, total_appends + 1)))
        self.assertEqual(self.log.get_highest_index(), total_appends)

if __name__ == "__main__":
    unittest.main()