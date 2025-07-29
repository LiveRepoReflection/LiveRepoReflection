import unittest
import math
from network_robust_routing import best_path_reliability

class TestNetworkRobustRouting(unittest.TestCase):
    def assertFloatAlmostEqual(self, first, second, tol=1e-9):
        self.assertTrue(abs(first - second) < tol, f"{first} not within {tol} of {second}")

    def test_direct_edge_meets_bandwidth(self):
        # Two nodes with a direct edge that meets the bandwidth requirement.
        n = 2
        edges = [(0, 1, 100, 0.1)]
        s = 0
        d = 1
        b = 50
        # Reliability: (1 - 0.1) = 0.9.
        expected = 0.9
        result = best_path_reliability(n, edges, s, d, b)
        self.assertFloatAlmostEqual(result, expected)

    def test_direct_edge_fails_bandwidth(self):
        # Direct edge does not meet the bandwidth requirement.
        n = 2
        edges = [(0, 1, 40, 0.1)]
        s = 0
        d = 1
        b = 50
        expected = 0.0
        result = best_path_reliability(n, edges, s, d, b)
        self.assertFloatAlmostEqual(result, expected)

    def test_multiple_paths_choose_best_reliability(self):
        # Multiple paths exist; choose the one with the highest reliability.
        n = 4
        edges = [
            (0, 1, 100, 0.1),
            (0, 2, 50, 0.2),
            (1, 2, 80, 0.05),
            (1, 3, 120, 0.15),
            (2, 3, 60, 0.08)
        ]
        s = 0
        d = 3
        b = 60
        # Valid paths:
        # Path 0->1->3: min bandwidth = min(100, 120) = 100, reliability = 0.9 * 0.85 = 0.765
        # Path 0->1->2->3: min bandwidth = min(100, 80, 60) = 60, reliability = 0.9 * 0.95 * 0.92 = 0.7866
        # Note: Path 0->2->3 fails the bandwidth requirement because min bandwidth = min(50, 60) = 50.
        expected = 0.9 * 0.95 * 0.92  # 0.7866
        result = best_path_reliability(n, edges, s, d, b)
        self.assertFloatAlmostEqual(result, expected)

    def test_path_not_existing(self):
        # No valid path from source to destination.
        n = 3
        edges = [
            (0, 1, 100, 0.2),
            (1, 2, 100, 0.2)
        ]
        s = 0
        d = 3
        b = 50
        expected = 0.0
        result = best_path_reliability(n, edges, s, d, b)
        self.assertFloatAlmostEqual(result, expected)

    def test_multiple_edges_single_valid_path(self):
        # Only one specific path meets the bandwidth requirement.
        n = 5
        edges = [
            (0, 1, 100, 0.1),
            (1, 2, 70, 0.2),
            (0, 3, 90, 0.05),
            (3, 2, 65, 0.1),
            (2, 4, 80, 0.05),
            (1, 4, 50, 0.3)
        ]
        s = 0
        d = 4
        b = 70
        # Valid path:
        # Path 0->1->2->4: min bandwidth = min(100, 70, 80) = 70, reliability = 0.9 * 0.8 * 0.95 = 0.684
        expected = 0.9 * 0.8 * 0.95
        result = best_path_reliability(n, edges, s, d, b)
        self.assertFloatAlmostEqual(result, expected)

    def test_large_network(self):
        # Create a larger network (ring topology) to verify efficiency.
        n = 10
        edges = []
        for i in range(n):
            u = i
            v = (i + 1) % n
            edges.append((u, v, 100, 0.1))
        s = 0
        d = 5
        b = 100
        # Only valid path: traverse the ring from 0 to 5 using 5 edges.
        expected = 0.9 ** 5
        result = best_path_reliability(n, edges, s, d, b)
        self.assertFloatAlmostEqual(result, expected)

if __name__ == '__main__':
    unittest.main()