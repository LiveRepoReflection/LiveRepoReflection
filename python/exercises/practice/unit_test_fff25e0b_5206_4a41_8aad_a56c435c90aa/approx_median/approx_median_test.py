import unittest
from approx_median import approximate_median

def compute_true_median(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 0:
        return None
    if n % 2 == 1:
        return float(sorted_data[n // 2])
    else:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2.0

class TestApproxMedian(unittest.TestCase):
    def test_single_worker_single_value(self):
        worker_data = [[5]]
        epsilon = 0.1
        result = approximate_median(worker_data, epsilon)
        self.assertEqual(result, 5)

    def test_multiple_workers(self):
        worker_data = [[1, 5, 2, 8], [9, 3, 7, 4], [6, 10]]
        epsilon = 0.1
        total_data = []
        for node in worker_data:
            total_data.extend(node)
        true_median = compute_true_median(total_data)
        result = approximate_median(worker_data, epsilon)
        tolerance = epsilon * len(total_data)
        self.assertTrue(abs(result - true_median) <= tolerance,
                        f"Result {result} is not within tolerance {tolerance} of true median {true_median}")

    def test_empty_worker_data(self):
        worker_data = [[], []]
        epsilon = 0.1
        result = approximate_median(worker_data, epsilon)
        self.assertIsNone(result, "Expected None for worker data with all empty lists")

    def test_all_workers_empty(self):
        worker_data = []
        epsilon = 0.1
        result = approximate_median(worker_data, epsilon)
        self.assertIsNone(result, "Expected None for empty worker data list")

    def test_epsilon_zero_with_odd_count(self):
        # For epsilon = 0, the approximate median must be exactly equal to the true median.
        worker_data = [[1, 3, 5, 7, 9]]
        epsilon = 0.0
        total_data = []
        for node in worker_data:
            total_data.extend(node)
        true_median = compute_true_median(total_data)
        result = approximate_median(worker_data, epsilon)
        self.assertEqual(result, int(true_median),
                         f"Expected exact median {true_median} when epsilon is 0, got {result}")

    def test_sparse_data(self):
        worker_data = [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10], []]
        epsilon = 0.2
        total_data = []
        for node in worker_data:
            total_data.extend(node)
        true_median = compute_true_median(total_data)
        result = approximate_median(worker_data, epsilon)
        tolerance = epsilon * len(total_data)
        self.assertTrue(abs(result - true_median) <= tolerance,
                        f"Result {result} is not within tolerance {tolerance} of true median {true_median}")

if __name__ == '__main__':
    unittest.main()