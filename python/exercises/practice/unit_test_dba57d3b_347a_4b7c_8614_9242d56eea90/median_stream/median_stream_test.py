import unittest
import math
from median_stream import process_median_stream

def interleaved_stream(data_streams):
    """
    Interleave the elements from data_streams in round-robin order.
    """
    result = []
    indices = [0] * len(data_streams)
    remaining = True
    while remaining:
        remaining = False
        for i, stream in enumerate(data_streams):
            if indices[i] < len(stream):
                result.append(stream[indices[i]])
                indices[i] += 1
                remaining = True
    return result

def exact_median(arr):
    """
    Compute the exact median of sorted list arr.
    """
    sorted_arr = sorted(arr)
    n = len(sorted_arr)
    if n % 2 == 1:
        return float(sorted_arr[n // 2])
    else:
        return (sorted_arr[n // 2 - 1] + sorted_arr[n // 2]) / 2.0

class TestMedianStream(unittest.TestCase):

    def test_single_worker(self):
        # Single worker with a simple increasing sequence
        N = 1
        epsilon = 0.01
        data_streams = [
            [1, 3, 5, 7, 9]
        ]
        # Global order is just the list itself.
        global_stream = data_streams[0]
        # Prepare queries at different timestamps.
        queries = [1, 3, 5]
        expected = []
        for q in queries:
            sub_stream = global_stream[:q]
            expected.append(exact_median(sub_stream))
        
        # Process the simulated distributed system.
        result = process_median_stream(N, epsilon, data_streams, queries)
        self.assertEqual(len(result), len(expected))
        for r, e in zip(result, expected):
            self.assertTrue(math.isclose(r, e, abs_tol=epsilon),
                            f"Expected {e} within tolerance {epsilon}, got {r}")

    def test_multiple_workers_round_robin(self):
        # Multiple workers with interleaved sequences.
        N = 3
        epsilon = 0.05
        data_streams = [
            [5, 2, 9],
            [1, 7, 4],
            [8, 3, 6]
        ]
        # Global stream via round-robin interleaving.
        global_stream = interleaved_stream(data_streams)
        # Choose queries that cover various points in the merged stream.
        queries = [2, 5, 7, 9]
        expected = []
        for q in queries:
            sub_stream = global_stream[:q]
            expected.append(exact_median(sub_stream))
        
        result = process_median_stream(N, epsilon, data_streams, queries)
        self.assertEqual(len(result), len(expected))
        for idx, (res_val, exp_val) in enumerate(zip(result, expected)):
            self.assertTrue(math.isclose(res_val, exp_val, abs_tol=epsilon),
                            f"Query index {idx}: Expected median close to {exp_val}, got {res_val}")

    def test_non_uniform_streams(self):
        # Test with streams of different lengths.
        N = 4
        epsilon = 0.1
        data_streams = [
            [10, 20, 30],
            [15, 25],
            [5, 35, 45, 55],
            [40]
        ]
        # Global stream: interleaved round-robin.
        global_stream = interleaved_stream(data_streams)
        queries = [1, 3, 6, len(global_stream)]
        expected = []
        for q in queries:
            sub_stream = global_stream[:q]
            expected.append(exact_median(sub_stream))
        
        result = process_median_stream(N, epsilon, data_streams, queries)
        self.assertEqual(len(result), len(expected))
        for idx, (res_val, exp_val) in enumerate(zip(result, expected)):
            self.assertTrue(math.isclose(res_val, exp_val, abs_tol=epsilon),
                            f"At query {idx} expected median around {exp_val} within tolerance {epsilon}, got {res_val}")

    def test_large_data_streams(self):
        # Test with larger streams to simulate higher load.
        N = 5
        epsilon = 0.05
        # Generate streams with varying ranges.
        data_streams = []
        for i in range(N):
            # Each stream: 100 numbers, simple pattern.
            stream = [j + i*10 for j in range(100)]
            data_streams.append(stream)
        
        global_stream = interleaved_stream(data_streams)
        # Create queries at various intervals.
        total = len(global_stream)
        queries = [1, total // 4, total // 2, total - 1, total]
        expected = []
        for q in queries:
            sub_stream = global_stream[:q]
            expected.append(exact_median(sub_stream))
        
        result = process_median_stream(N, epsilon, data_streams, queries)
        self.assertEqual(len(result), len(expected))
        for idx, (r_val, e_val) in enumerate(zip(result, expected)):
            self.assertTrue(math.isclose(r_val, e_val, abs_tol=epsilon),
                            f"Large stream query index {idx}: Expected median near {e_val}, got {r_val}")

    def test_epsilon_tolerance(self):
        # Test ensuring reported median respects epsilon tolerance.
        N = 2
        epsilon = 0.2
        data_streams = [
            [3, 1, 4, 1, 5, 9],
            [2, 6, 5, 3, 5]
        ]
        global_stream = interleaved_stream(data_streams)
        queries = [5, 10, 11]
        expected = []
        for q in queries:
            sub_stream = global_stream[:q]
            expected.append(exact_median(sub_stream))
        
        result = process_median_stream(N, epsilon, data_streams, queries)
        self.assertEqual(len(result), len(expected))
        for idx, (median_val, exp_median) in enumerate(zip(result, expected)):
            diff = abs(median_val - exp_median)
            self.assertTrue(diff <= epsilon,
                            f"Query {idx}: Expected median {exp_median} +/- {epsilon}, but got {median_val} (diff {diff})")

if __name__ == '__main__':
    unittest.main()