import unittest
from dex_matching import process_operations

class DexMatchingEngineTest(unittest.TestCase):
    def test_simple_market_buy(self):
        operations = [
            "LIMIT SELL 1 100 10",
            "MARKET BUY 5"
        ]
        expected_output = [[(1, 100, 5)]]
        self.assertEqual(process_operations(operations), expected_output)

    def test_simple_market_sell(self):
        operations = [
            "LIMIT BUY 1 100 10",
            "MARKET SELL 5"
        ]
        expected_output = [[(1, 100, 5)]]
        self.assertEqual(process_operations(operations), expected_output)

    def test_example_case(self):
        operations = [
            "LIMIT BUY 1 100 10",
            "LIMIT SELL 2 101 5",
            "MARKET BUY 5",
            "LIMIT SELL 3 99 7",
            "MARKET SELL 3",
            "CANCEL 2",
            "MARKET BUY 5"
        ]
        expected_output = [
            [(2, 101, 5)],
            [(1, 100, 3)],
            [(3, 99, 5)]
        ]
        self.assertEqual(process_operations(operations), expected_output)

    def test_market_buy_multiple_price_levels(self):
        operations = [
            "LIMIT SELL 1 100 5",
            "LIMIT SELL 2 101 5",
            "LIMIT SELL 3 102 5",
            "MARKET BUY 12"
        ]
        expected_output = [[(1, 100, 5), (2, 101, 5), (3, 102, 2)]]
        self.assertEqual(process_operations(operations), expected_output)

    def test_market_sell_multiple_price_levels(self):
        operations = [
            "LIMIT BUY 1 102 5",
            "LIMIT BUY 2 101 5",
            "LIMIT BUY 3 100 5",
            "MARKET SELL 12"
        ]
        expected_output = [[(1, 102, 5), (2, 101, 5), (3, 100, 2)]]
        self.assertEqual(process_operations(operations), expected_output)

    def test_cancel_order(self):
        operations = [
            "LIMIT BUY 1 100 10",
            "CANCEL 1",
            "MARKET SELL 5"
        ]
        expected_output = [[]]  # No trades executed
        self.assertEqual(process_operations(operations), expected_output)

    def test_price_time_priority_buy(self):
        operations = [
            "LIMIT BUY 1 100 5",
            "LIMIT BUY 2 100 5",  # Same price, later time
            "LIMIT BUY 3 101 5",  # Better price
            "MARKET SELL 10"
        ]
        expected_output = [[(3, 101, 5), (1, 100, 5)]]  # Order 3 first (better price), then 1 (earlier time)
        self.assertEqual(process_operations(operations), expected_output)

    def test_price_time_priority_sell(self):
        operations = [
            "LIMIT SELL 1 100 5",
            "LIMIT SELL 2 100 5",  # Same price, later time
            "LIMIT SELL 3 99 5",   # Better price
            "MARKET BUY 10"
        ]
        expected_output = [[(3, 99, 5), (1, 100, 5)]]  # Order 3 first (better price), then 1 (earlier time)
        self.assertEqual(process_operations(operations), expected_output)

    def test_partial_fills(self):
        operations = [
            "LIMIT BUY 1 100 10",
            "MARKET SELL 5",      # Partially fills order 1
            "MARKET SELL 3"       # Further partially fills order 1
        ]
        expected_output = [
            [(1, 100, 5)],
            [(1, 100, 3)]
        ]
        self.assertEqual(process_operations(operations), expected_output)

    def test_large_order_book(self):
        operations = ["LIMIT BUY 1 100 10"]
        
        # Add 1000 sell orders with decreasing prices
        for i in range(2, 1002):
            operations.append(f"LIMIT SELL {i} {200-i//5} 1")
        
        # Market buy should match with lowest-priced sell orders first
        operations.append("MARKET BUY 5")
        
        results = process_operations(operations)
        
        # Check that we got exactly 5 matches
        trades = results[-1]
        self.assertEqual(len(trades), 5)
        
        # Check that prices are in ascending order (best prices first)
        prices = [trade[1] for trade in trades]
        self.assertEqual(prices, sorted(prices))

    def test_invalid_cancel(self):
        operations = [
            "LIMIT BUY 1 100 10",
            "CANCEL 999",  # Non-existent order
            "MARKET SELL 5"
        ]
        expected_output = [[(1, 100, 5)]]  # Order 1 should still be there
        self.assertEqual(process_operations(operations), expected_output)

    def test_market_order_partial_execution(self):
        operations = [
            "LIMIT SELL 1 100 5",
            "MARKET BUY 10"  # Only 5 units available
        ]
        expected_output = [[(1, 100, 5)]]  # Should execute only what's available
        self.assertEqual(process_operations(operations), expected_output)

    def test_stress_test_many_operations(self):
        operations = []
        # Add 1000 buy orders
        for i in range(1, 1001):
            operations.append(f"LIMIT BUY {i} {50 + i % 10} {i % 5 + 1}")
        
        # Add 1000 sell orders
        for i in range(1001, 2001):
            operations.append(f"LIMIT SELL {i} {60 + i % 10} {i % 5 + 1}")
        
        # Cancel some orders
        for i in range(1, 2001, 10):
            operations.append(f"CANCEL {i}")
        
        # Execute some market orders
        operations.append("MARKET BUY 50")
        operations.append("MARKET SELL 50")
        
        # We're just testing that this completes without errors
        # The exact output depends on the implementation details
        results = process_operations(operations)
        self.assertEqual(len(results), 2)  # Should have results for the two market orders

if __name__ == '__main__':
    unittest.main()