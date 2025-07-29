import unittest
from martian_network import find_most_reliable_path

class MartianNetworkTest(unittest.TestCase):
    def test_direct_vs_indirect(self):
        # Test comparing direct vs indirect path reliability and latency.
        N = 3
        edges = [
            (0, 1, lambda sol: sol + 1),
            (1, 2, lambda sol: sol + 2),
            (0, 2, lambda sol: sol + 3)
        ]
        failure_probabilities = [0.1, 0.2, 0.3]
        s, d = 0, 2
        start_sol, end_sol = 1, 2
        # For direct path [0,2]:
        # Reliability of node 0 over sols [1,2]: (1-0.1)^2 = 0.9^2 = 0.81
        # For indirect path [0,1,2]:
        # Reliability of nodes 0 and 1: (0.9*0.8)^2 = (0.72)^2 = 0.5184
        # Thus, direct path should be selected.
        expected_path = [0, 2]
        expected_reliability = 0.9**2
        expected_latency = sum((sol + 3) for sol in range(start_sol, end_sol + 1))
        result = find_most_reliable_path(N, edges, failure_probabilities, s, d, start_sol, end_sol)
        self.assertEqual(result[0], expected_path)
        self.assertAlmostEqual(result[1], expected_reliability, places=5)
        self.assertEqual(result[2], expected_latency)

    def test_tie_break_on_latency(self):
        # Test tie-breaker scenario where two paths have equal reliability.
        N = 4
        edges = [
            (0, 1, lambda sol: 2),
            (1, 3, lambda sol: 3),
            (0, 2, lambda sol: 1),
            (2, 3, lambda sol: 5)
        ]
        failure_probabilities = [0.1, 0.2, 0.2, 0.4]
        s, d = 0, 3
        start_sol, end_sol = 0, 0  # Single sol, so latency values are constant.
        # Calculate reliability: For both paths [0,1,3] and [0,2,3]
        # Reliability = (1-0.1) * (1-0.2) = 0.9 * 0.8 = 0.72.
        # Latency for [0,1,3]: 2 + 3 = 5, and for [0,2,3]: 1 + 5 = 6.
        # Expected path is [0,1,3] due to lower latency.
        expected_path = [0, 1, 3]
        expected_reliability = 0.9 * 0.8
        expected_latency = 2 + 3
        result = find_most_reliable_path(N, edges, failure_probabilities, s, d, start_sol, end_sol)
        self.assertEqual(result[0], expected_path)
        self.assertAlmostEqual(result[1], expected_reliability, places=5)
        self.assertEqual(result[2], expected_latency)

    def test_no_path(self):
        # Test when no path exists from source to destination.
        N = 3
        edges = [
            (0, 1, lambda sol: 1),
            (1, 0, lambda sol: 1)
        ]
        failure_probabilities = [0.1, 0.2, 0.3]
        s, d = 0, 2
        start_sol, end_sol = 0, 1
        expected = ([], 0.0, 0)
        result = find_most_reliable_path(N, edges, failure_probabilities, s, d, start_sol, end_sol)
        self.assertEqual(result, expected)

    def test_cycle_graph(self):
        # Test graph with cycles to ensure algorithm avoids infinite loops.
        N = 4
        edges = [
            (0, 1, lambda sol: 1),
            (1, 2, lambda sol: 1),
            (2, 1, lambda sol: 1),  # Cycle between nodes 1 and 2.
            (2, 3, lambda sol: 1)
        ]
        failure_probabilities = [0.0, 0.0, 0.0, 0.0]
        s, d = 0, 3
        start_sol, end_sol = 0, 2  # Three sols: 0, 1, 2.
        # Expected path is [0, 1, 2, 3]
        # Each edge latency = sum_{sol=0}^{2} 1 = 3, so total latency = 3*3 = 9.
        expected_path = [0, 1, 2, 3]
        expected_latency = 3 * 3
        expected_reliability = 1.0
        result = find_most_reliable_path(N, edges, failure_probabilities, s, d, start_sol, end_sol)
        self.assertEqual(result[0], expected_path)
        self.assertAlmostEqual(result[1], expected_reliability, places=5)
        self.assertEqual(result[2], expected_latency)

    def test_varying_sol_latency(self):
        # Test with non-linear latency functions over multiple sols.
        N = 3
        edges = [
            (0, 1, lambda sol: sol * sol),
            (1, 2, lambda sol: 2 * sol + 1),
            (0, 2, lambda sol: 3 * sol)
        ]
        failure_probabilities = [0.05, 0.1, 0.15]
        s, d = 0, 2
        start_sol, end_sol = 2, 4  # Sols: 2, 3, 4
        # Calculate latency for direct path [0,2] over sols 2,3,4.
        direct_latency = sum(3 * sol for sol in range(start_sol, end_sol + 1))
        direct_reliability = (1 - 0.05) ** (end_sol - start_sol + 1)
        # For indirect path [0,1,2]:
        latency_01 = sum(sol * sol for sol in range(start_sol, end_sol + 1))
        latency_12 = sum(2 * sol + 1 for sol in range(start_sol, end_sol + 1))
        indirect_latency = latency_01 + latency_12
        indirect_reliability = ((1 - 0.05) * (1 - 0.1)) ** (end_sol - start_sol + 1)
        # Determine which path is more reliable. In case of a tie, lower latency wins.
        if direct_reliability > indirect_reliability:
            expected_path = [0, 2]
            expected_reliability = direct_reliability
            expected_latency = direct_latency
        elif direct_reliability < indirect_reliability:
            expected_path = [0, 1, 2]
            expected_reliability = indirect_reliability
            expected_latency = indirect_latency
        else:
            if direct_latency <= indirect_latency:
                expected_path = [0, 2]
                expected_reliability = direct_reliability
                expected_latency = direct_latency
            else:
                expected_path = [0, 1, 2]
                expected_reliability = indirect_reliability
                expected_latency = indirect_latency

        result = find_most_reliable_path(N, edges, failure_probabilities, s, d, start_sol, end_sol)
        self.assertEqual(result[0], expected_path)
        self.assertAlmostEqual(result[1], expected_reliability, places=5)
        self.assertEqual(result[2], expected_latency)

if __name__ == '__main__':
    unittest.main()