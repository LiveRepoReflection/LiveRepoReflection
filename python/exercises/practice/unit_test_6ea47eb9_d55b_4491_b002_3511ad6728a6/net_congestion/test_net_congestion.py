import unittest
from net_congestion import simulate_network

class TestNetCongestion(unittest.TestCase):
    def test_basic_two_node_network(self):
        N = 2
        links = [(0, 1, 10)]
        initial_rates = [5, 5]
        routes = [[[0, 1]], [[1]]]
        T = 1
        alpha = 1
        beta = 0.5
        max_rate = 10
        
        expected = [6, 6]
        result = simulate_network(N, links, initial_rates, routes, T, alpha, beta, max_rate)
        self.assertEqual(len(result), N)
        self.assertEqual(result, expected)

    def test_congested_link(self):
        N = 3
        links = [(0, 1, 10), (1, 2, 5)]
        initial_rates = [7, 3, 2]
        routes = [[[0, 1, 2]], [[1, 2]], [[2]]]
        T = 1
        alpha = 1
        beta = 0.5
        max_rate = 10
        
        result = simulate_network(N, links, initial_rates, routes, T, alpha, beta, max_rate)
        self.assertEqual(len(result), N)
        # Rates should decrease due to congestion on link (1,2)
        self.assertLess(result[0], initial_rates[0])
        self.assertLess(result[1], initial_rates[1])

    def test_maximum_rate_constraint(self):
        N = 2
        links = [(0, 1, 100)]
        initial_rates = [95, 95]
        routes = [[[0, 1]], [[1]]]
        T = 2
        alpha = 10
        beta = 0.5
        max_rate = 100
        
        result = simulate_network(N, links, initial_rates, routes, T, alpha, beta, max_rate)
        self.assertTrue(all(rate <= max_rate for rate in result))

    def test_minimum_rate_constraint(self):
        N = 2
        links = [(0, 1, 5)]
        initial_rates = [2, 2]
        routes = [[[0, 1]], [[1]]]
        T = 3
        alpha = 1
        beta = 0.1
        max_rate = 10
        
        result = simulate_network(N, links, initial_rates, routes, T, alpha, beta, max_rate)
        self.assertTrue(all(rate >= 0 for rate in result))

    def test_complex_network(self):
        N = 5
        links = [(0, 1, 10), (1, 2, 8), (2, 3, 5), (3, 4, 7), (0, 2, 6), (1, 3, 4)]
        initial_rates = [5, 4, 3, 2, 1]
        routes = [
            [[0, 1, 2], [0, 2]],
            [[1, 2], [1, 3]],
            [[2, 3]],
            [[3, 4]],
            [[4]]
        ]
        T = 5
        alpha = 1
        beta = 0.5
        max_rate = 15
        
        result = simulate_network(N, links, initial_rates, routes, T, alpha, beta, max_rate)
        self.assertEqual(len(result), N)
        self.assertTrue(all(0 <= rate <= max_rate for rate in result))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            # Test negative number of nodes
            simulate_network(-1, [], [], [], 1, 1, 0.5, 10)
        
        with self.assertRaises(ValueError):
            # Test invalid beta value
            simulate_network(2, [(0,1,10)], [5,5], [[[0,1]], [[1]]], 1, 1, 1.5, 10)
        
        with self.assertRaises(ValueError):
            # Test invalid alpha value
            simulate_network(2, [(0,1,10)], [5,5], [[[0,1]], [[1]]], 1, -1, 0.5, 10)
        
        with self.assertRaises(ValueError):
            # Test invalid max_rate
            simulate_network(2, [(0,1,10)], [5,5], [[[0,1]], [[1]]], 1, 1, 0.5, -10)

    def test_empty_network(self):
        N = 1
        links = []
        initial_rates = [5]
        routes = [[[]]]
        T = 1
        alpha = 1
        beta = 0.5
        max_rate = 10
        
        result = simulate_network(N, links, initial_rates, routes, T, alpha, beta, max_rate)
        self.assertEqual(result, [6])  # Should increase by alpha since no congestion

    def test_multiple_time_steps(self):
        N = 2
        links = [(0, 1, 10)]
        initial_rates = [5, 5]
        routes = [[[0, 1]], [[1]]]
        T = 5
        alpha = 1
        beta = 0.5
        max_rate = 10
        
        result = simulate_network(N, links, initial_rates, routes, T, alpha, beta, max_rate)
        self.assertEqual(len(result), N)
        # After multiple steps, rates should have changed significantly
        self.assertNotEqual(result, initial_rates)

if __name__ == '__main__':
    unittest.main()