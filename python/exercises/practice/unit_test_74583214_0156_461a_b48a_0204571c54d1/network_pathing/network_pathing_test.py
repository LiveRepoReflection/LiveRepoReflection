import unittest
from network_pathing import optimal_path_cost

class TestNetworkPathing(unittest.TestCase):
    def test_simple_network(self):
        n = 3
        links = [(0, 1, 5), (1, 2, 3)]
        risk_factors = [1, 2, 1]
        s = 0
        d = 2
        risk_weight = 1.0
        expected = 5 + 3 + (1 + 2 + 1) * 1.0
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

    def test_disconnected_network(self):
        n = 4
        links = [(0, 1, 2), (2, 3, 3)]
        risk_factors = [1, 1, 1, 1]
        s = 0
        d = 3
        risk_weight = 0.5
        self.assertEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), -1)

    def test_multiple_paths(self):
        n = 4
        links = [(0, 1, 3), (0, 2, 5), (1, 3, 2), (2, 3, 1)]
        risk_factors = [2, 3, 1, 4]
        s = 0
        d = 3
        risk_weight = 2.0
        expected = min(
            3 + 2 + (2 + 3 + 4) * 2.0,
            5 + 1 + (2 + 1 + 4) * 2.0
        )
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

    def test_same_source_and_destination(self):
        n = 3
        links = [(0, 1, 2), (1, 2, 3)]
        risk_factors = [1, 1, 1]
        s = 1
        d = 1
        risk_weight = 0.5
        expected = 0 + (1) * 0.5
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

    def test_large_risk_weight(self):
        n = 3
        links = [(0, 1, 1), (1, 2, 1), (0, 2, 5)]
        risk_factors = [10, 1, 10]
        s = 0
        d = 2
        risk_weight = 100.0
        expected = 5 + (10 + 10) * 100.0  # Direct path is better despite higher latency
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

    def test_no_risk_consideration(self):
        n = 4
        links = [(0, 1, 2), (0, 2, 3), (1, 3, 3), (2, 3, 1)]
        risk_factors = [5, 5, 5, 5]
        s = 0
        d = 3
        risk_weight = 0.0
        expected = 3 + 1  # Shortest path by latency only
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

    def test_multiple_links_between_nodes(self):
        n = 2
        links = [(0, 1, 2), (0, 1, 5)]
        risk_factors = [1, 2]
        s = 0
        d = 1
        risk_weight = 1.0
        expected = 2 + (1 + 2) * 1.0  # Should choose lower latency link
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

    def test_self_loop(self):
        n = 2
        links = [(0, 0, 1), (0, 1, 2)]
        risk_factors = [1, 2]
        s = 0
        d = 1
        risk_weight = 1.0
        expected = 2 + (1 + 2) * 1.0  # Should ignore self-loop
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

    def test_large_network(self):
        n = 100
        links = [(i, i+1, 1) for i in range(99)] + [(0, 99, 100)]
        risk_factors = [1] * 100
        s = 0
        d = 99
        risk_weight = 0.1
        expected = min(
            99 * 1 + sum([1] * 100) * 0.1,
            100 + (1 + 1) * 0.1
        )
        self.assertAlmostEqual(optimal_path_cost(n, links, risk_factors, s, d, risk_weight), expected)

if __name__ == '__main__':
    unittest.main()