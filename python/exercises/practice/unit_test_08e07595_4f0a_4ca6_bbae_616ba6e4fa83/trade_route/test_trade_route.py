import unittest
from decimal import Decimal
from trade_route import find_optimal_trade_route

class TestTradeRoute(unittest.TestCase):
    def test_direct_path(self):
        graph = {
            "BTC": [("USD", 19000)],
            "USD": [("BTC", 1/19000)]
        }
        self.assertEqual(
            find_optimal_trade_route(graph, "BTC", "USD", 1.0, 1, 0),
            19000.0
        )

    def test_two_hop_path(self):
        graph = {
            "BTC": [("ETH", 15.0)],
            "ETH": [("USD", 1500.0)],
            "USD": [("BTC", 1/20000)]
        }
        # BTC -> ETH -> USD: 1 BTC -> 15 ETH -> 22500 USD
        self.assertEqual(
            find_optimal_trade_route(graph, "BTC", "USD", 1.0, 2, 0),
            22500.0
        )

    def test_arbitrage_cycle(self):
        graph = {
            "BTC": [("ETH", 15.0), ("USD", 19000)],
            "ETH": [("USD", 1600.0), ("BTC", 0.06)],
            "USD": [("BTC", 1/20000), ("ETH", 1/1500)]
        }
        # Should find arbitrage opportunity if it exists within max_hops
        result = find_optimal_trade_route(graph, "BTC", "USD", 1.0, 5, 0)
        self.assertGreater(result, 19000.0)  # Should be better than direct path

    def test_no_path_exists(self):
        graph = {
            "BTC": [("ETH", 15.0)],
            "ETH": [("BTC", 0.06)],
            "USD": []
        }
        self.assertEqual(
            find_optimal_trade_route(graph, "BTC", "USD", 1.0, 3, 0),
            0.0
        )

    def test_same_currency(self):
        graph = {
            "BTC": [("ETH", 15.0)],
            "ETH": [("BTC", 0.06)]
        }
        self.assertEqual(
            find_optimal_trade_route(graph, "BTC", "BTC", 1.0, 3, 0),
            1.0
        )

    def test_zero_initial_amount(self):
        graph = {
            "BTC": [("USD", 19000)],
            "USD": [("BTC", 1/19000)]
        }
        self.assertEqual(
            find_optimal_trade_route(graph, "BTC", "USD", 0.0, 1, 0),
            0.0
        )

    def test_minimum_profit_threshold(self):
        graph = {
            "BTC": [("USD", 19000)],
            "USD": [("BTC", 1/19000)]
        }
        # Should return 0 if profit doesn't meet threshold
        self.assertEqual(
            find_optimal_trade_route(graph, "BTC", "USD", 1.0, 1, 20000),
            0.0
        )

    def test_max_hops_limit(self):
        graph = {
            "BTC": [("ETH", 15.0)],
            "ETH": [("USDT", 1500.0)],
            "USDT": [("USD", 1.0)],
            "USD": [("BTC", 1/20000)]
        }
        # Path exists but requires 3 hops, max_hops = 2
        self.assertEqual(
            find_optimal_trade_route(graph, "BTC", "USD", 1.0, 2, 0),
            0.0
        )

    def test_numerical_precision(self):
        graph = {
            "BTC": [("USD", 0.000000001)],
            "USD": [("BTC", 1000000000)]
        }
        result = find_optimal_trade_route(graph, "BTC", "USD", 1.0, 1, 0)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_large_graph(self):
        # Create a large graph with 100 currencies
        graph = {}
        for i in range(100):
            curr1 = f"CURR{i}"
            graph[curr1] = []
            for j in range(100):
                if i != j:
                    curr2 = f"CURR{j}"
                    graph[curr1].append((curr2, 1.0))
        
        result = find_optimal_trade_route(graph, "CURR0", "CURR99", 1.0, 3, 0)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

if __name__ == '__main__':
    unittest.main()