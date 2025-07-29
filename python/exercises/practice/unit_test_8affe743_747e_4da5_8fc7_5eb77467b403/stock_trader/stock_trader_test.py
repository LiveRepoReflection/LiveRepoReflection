import unittest
from stock_trader import max_profit

class StockTraderTest(unittest.TestCase):
    def test_basic_profitable_transactions(self):
        # prices: [100, 180, 260, 310, 40, 535, 695]
        # K=2, fee=10, C=100
        # Expected: First transaction: buy at 100, sell at 310 => profit 310-100-10 = 200, C becomes 300.
        # Second transaction: buy at 40, sell at 695 => profit 695-40-10 = 645, C becomes 300+645 = 945.
        prices = [100, 180, 260, 310, 40, 535, 695]
        K = 2
        fee = 10
        C = 100
        expected = 945
        self.assertEqual(max_profit(K, prices, fee, C), expected)

    def test_monotonically_decreasing_prices(self):
        # Prices constantly decreasing, so no profitable transaction exists.
        prices = [310, 260, 180, 100]
        K = 2
        fee = 10
        C = 500
        expected = 500  # No transaction, capital remains the same.
        self.assertEqual(max_profit(K, prices, fee, C), expected)

    def test_empty_prices(self):
        prices = []
        K = 2
        fee = 10
        C = 500
        expected = 500  # No trading possible.
        self.assertEqual(max_profit(K, prices, fee, C), expected)

    def test_high_fee_transactions(self):
        # Transaction fee is high resulting in no profitable transactions.
        prices = [100, 120, 130, 150]
        K = 2
        fee = 50
        C = 200
        expected = 200  # No transaction occurs
        self.assertEqual(max_profit(K, prices, fee, C), expected)

    def test_insufficient_initial_capital(self):
        # Initial capital is not enough to buy any stock.
        prices = [200, 220, 210, 250]
        K = 2
        fee = 10
        C = 150
        expected = 150  # Capital remains unchanged.
        self.assertEqual(max_profit(K, prices, fee, C), expected)

    def test_single_profitable_transaction(self):
        # Simple scenario where one transaction is beneficial.
        prices = [1, 5, 4]
        K = 2
        fee = 1
        C = 10
        # Only transaction: buy at 1, sell at 5 remains profitable 
        # Profit = 5-1-1 = 3 => Final capital = 10+3=13.
        expected = 13
        self.assertEqual(max_profit(K, prices, fee, C), expected)

    def test_multiple_transactions_with_limit(self):
        # More complex case with multiple potential transactions.
        prices = [3, 8, 2, 5, 7, 4, 10]
        K = 3
        fee = 2
        C = 20
        # Best strategy:
        # Transaction1: Buy at 3, sell at 8 => profit = 8-3-2 = 3, new C = 23.
        # Transaction2: Buy at 2, sell at 7 => profit = 7-2-2 = 3, new C = 26.
        # Transaction3: Buy at 4, sell at 10 => profit = 10-4-2 = 4, new C = 30.
        expected = 30
        self.assertEqual(max_profit(K, prices, fee, C), expected)

    def test_no_transactions_allowed(self):
        # When K is 0, no transactions can be made.
        prices = [100, 200]
        K = 0
        fee = 10
        C = 100
        expected = 100  # Capital remains unchanged.
        self.assertEqual(max_profit(K, prices, fee, C), expected)
        
if __name__ == '__main__':
    unittest.main()