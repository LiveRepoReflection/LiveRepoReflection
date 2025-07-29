import unittest
import math
import time
from parallel_data import process_data
from collections import OrderedDict

class TestParallelData(unittest.TestCase):
    def test_empty_data(self):
        def empty_generator():
            yield from []

        result = process_data(empty_generator(), 2)
        self.assertEqual(result, 0.0)

    def test_example_data(self):
        def example_data():
            data = [
                {"user_id": 1, "value": "4", "status": "active"},
                {"user_id": 2, "value": "9", "status": "inactive"},
                {"user_id": 1, "value": 4, "status": "active"},  # Duplicate after mapping
                {"user_id": 3, "value": "16", "status": "active"},
                {"user_id": 4, "value": None, "status": "active"},
                {"user_id": 5, "value": "abc", "status": "active"},
                {"user_id": 3, "value": "25", "status": "active"},  # Duplicate after mapping
            ]
            for item in data:
                yield item

        result = process_data(example_data(), 1)
        self.assertAlmostEqual(result, 2.2, places=5)

    def test_single_value(self):
        def single_value_generator():
            yield {"user_id": 1, "value": "9", "status": "active"}

        result = process_data(single_value_generator(), 3)
        self.assertEqual(result, 3.0)

    def test_all_inactive(self):
        def inactive_generator():
            data = [
                {"user_id": 1, "value": "4", "status": "inactive"},
                {"user_id": 2, "value": "9", "status": "inactive"},
                {"user_id": 3, "value": "16", "status": "inactive"},
            ]
            for item in data:
                yield item

        result = process_data(inactive_generator(), 2)
        self.assertEqual(result, 0.0)

    def test_all_filtered_out(self):
        def filtered_out_generator():
            data = [
                {"user_id": 1, "value": "4", "status": "inactive"},
                {"user_id": 2, "value": "9", "status": "inactive"},
                {"user_id": 3, "value": "16", "status": "inactive"},
            ]
            for item in data:
                yield item

        result = process_data(filtered_out_generator(), 1)
        self.assertEqual(result, 0.0)

    def test_large_data(self):
        def large_data_generator():
            # Generate 10,000 records
            for i in range(10000):
                status = "active" if i % 2 == 0 else "inactive"
                yield {"user_id": i % 100, "value": i, "status": status}

        start_time = time.time()
        result = process_data(large_data_generator(), 4)
        end_time = time.time()
        
        # Check that result is a float
        self.assertIsInstance(result, float)
        
        # Sanity check on result (we expect all even-numbered values to be processed)
        self.assertGreater(result, 0.0)
        
        # Time check for performance
        self.assertLess(end_time - start_time, 5.0, "Processing took too long")

    def test_error_handling(self):
        def problematic_data():
            data = [
                {"user_id": 1, "value": "4", "status": "active"},
                {"user_id": 2, "value": {}, "status": "active"},  # Dictionary value
                {"user_id": 3, "value": -9, "status": "active"},  # Negative value
                {"user_id": 4, "status": "active"},  # Missing value field
                {"user_id": 5, "value": "active"},  # Missing status field
                {"value": 16, "status": "active"},  # Missing user_id
                {"user_id": 6, "value": float('nan'), "status": "active"},  # NaN value
                {"user_id": 7, "value": float('inf'), "status": "active"},  # Inf value
            ]
            for item in data:
                yield item

        # Should handle all these problematic cases without crashing
        result = process_data(problematic_data(), 2)
        
        # Records 1, 3, and 4 should be processed
        # 2.0, 3.0, 0.0 -> average = 1.67
        self.assertIsInstance(result, float)

    def test_immediate_termination(self):
        def infinite_generator():
            i = 0
            while True:
                yield {"user_id": i, "value": i, "status": "active"}
                i += 1
        
        # The function should terminate even with an infinite generator
        start_time = time.time()
        try:
            # Using a short timeout to make sure it terminates
            result = process_data(infinite_generator(), 2, max_records=100)
            elapsed = time.time() - start_time
            self.assertLess(elapsed, 3.0, "Processing took too long")
        except Exception as e:
            self.fail(f"Function did not terminate properly: {e}")

    def test_complex_deduplication(self):
        def generate_duplicates():
            # Many duplicates with different formatting but same processed value
            data = [
                {"user_id": 1, "value": "4", "status": "active"},
                {"user_id": 1, "value": 4.0, "status": "active"},
                {"user_id": 1, "value": 4, "status": "active"},
                {"user_id": 2, "value": "9", "status": "active"},
                {"user_id": 2, "value": 9, "status": "active"},
                {"user_id": 3, "value": "16", "status": "active"},
                {"user_id": 3, "value": 16.0, "status": "active"},
            ]
            for item in data:
                yield item

        result = process_data(generate_duplicates(), 3)
        # Expected: only 3 unique (user_id, processed_value) pairs: (1, 2.0), (2, 3.0), (3, 4.0)
        self.assertAlmostEqual(result, 3.0, places=5)

    def test_multiprocess_correctness(self):
        def generate_data():
            for i in range(1000):
                yield {"user_id": i % 10, "value": i, "status": "active"}

        # Compare results with different numbers of processes
        result1 = process_data(generate_data(), 1)
        result2 = process_data(generate_data(), 2)
        result4 = process_data(generate_data(), 4)
        
        # Results should be the same regardless of process count
        self.assertAlmostEqual(result1, result2, places=5)
        self.assertAlmostEqual(result1, result4, places=5)

    def test_negative_values(self):
        def negative_values():
            data = [
                {"user_id": 1, "value": -4, "status": "active"},
                {"user_id": 2, "value": -9, "status": "active"},
                {"user_id": 3, "value": -16, "status": "active"},
            ]
            for item in data:
                yield item

        result = process_data(negative_values(), 2)
        # Expected: sqrt(abs(-4)) = 2.0, sqrt(abs(-9)) = 3.0, sqrt(abs(-16)) = 4.0
        # Average = (2.0 + 3.0 + 4.0) / 3 = 3.0
        self.assertEqual(result, 3.0)

if __name__ == '__main__':
    unittest.main()