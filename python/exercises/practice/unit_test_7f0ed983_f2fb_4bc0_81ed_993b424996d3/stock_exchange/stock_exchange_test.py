import unittest
from stock_exchange import Exchange

class StockExchangeTest(unittest.TestCase):
    def setUp(self):
        # Create a fresh instance of the Exchange for each test.
        self.engine = Exchange()

    def test_no_trade_for_standalone_order(self):
        # When there is no opposing order, no trade should occur.
        order = (100, 1678886400, "AAPL", "BUY", 100, 170.00)
        trades = self.engine.process_order(order)
        self.assertEqual(trades, [])

    def test_single_match_trade(self):
        # Test a scenario where a single incoming order matches an existing order.
        # 1. Add a BUY order.
        buy_order = (1, 1678886400, "AAPL", "BUY", 100, 170.00)
        trades = self.engine.process_order(buy_order)
        self.assertEqual(trades, [])
        # 2. Add a SELL order that matches the buy order.
        sell_order = (2, 1678886401, "AAPL", "SELL", 50, 165.00)
        trades = self.engine.process_order(sell_order)
        # Trade should occur at sell order's price for 50 shares.
        self.assertEqual(trades, [(1, 2, 50, 165.00)])
    
    def test_partial_fill_order(self):
        # Test partial fill where an order is only partially filled and the remainder stays.
        # 1. Add a BUY order of 100 shares.
        buy_order = (1, 1678886400, "AAPL", "BUY", 100, 170.00)
        trades = self.engine.process_order(buy_order)
        self.assertEqual(trades, [])
        # 2. Add a SELL order that partially fills the BUY order.
        sell_order = (2, 1678886401, "AAPL", "SELL", 60, 165.00)
        trades = self.engine.process_order(sell_order)
        # Trade: 60 shares executed.
        self.assertEqual(trades, [(1, 2, 60, 165.00)])
        # 3. Add another SELL order to fill remaining 40 shares.
        sell_order2 = (3, 1678886402, "AAPL", "SELL", 50, 165.00)
        trades = self.engine.process_order(sell_order2)
        # Only 40 shares can be matched from the remaining of BUY order.
        self.assertEqual(trades, [(1, 3, 40, 165.00)])
    
    def test_multiple_matches_across_orders(self):
        # Test scenario with multiple orders leading to several trades including partial fills.
        orders = [
            (1, 1678886400, "AAPL", "BUY", 100, 170.00),
            (2, 1678886401, "AAPL", "SELL", 50, 165.00),
            (3, 1678886402, "AAPL", "SELL", 60, 165.00),
            (4, 1678886403, "GOOG", "BUY", 20, 2500.00),
            (5, 1678886404, "GOOG", "SELL", 20, 2490.00),
            (6, 1678886405, "AAPL", "BUY", 60, 165.00)
        ]
        expected_trades = [
            [],  # Order 1: BUY order, added to order book, no match.
            [(1, 2, 50, 165.00)],  # Order 2: SELL matches with order 1 partially.
            [(1, 3, 50, 165.00)],  # Order 3: SELL matches with remaining 50 shares of order 1. 10 remain in order 3.
            [],  # Order 4: GOOG BUY order, no match.
            [(4, 5, 20, 2490.00)],  # Order 5: SELL matches with GOOG BUY order.
            [(6, 3, 10, 165.00)]   # Order 6: BUY order, matches with remaining 10 shares of order 3.
        ]
        results = []
        for order in orders:
            trades = self.engine.process_order(order)
            results.append(trades)
        self.assertEqual(results, expected_trades)
    
    def test_separate_stock_symbols(self):
        # Ensure orders for different stocks do not interfere.
        # For AAPL:
        aapl_buy = (10, 1678886400, "AAPL", "BUY", 100, 170.00)
        self.assertEqual(self.engine.process_order(aapl_buy), [])
        aapl_sell = (11, 1678886401, "AAPL", "SELL", 100, 165.00)
        trades_aapl = self.engine.process_order(aapl_sell)
        self.assertEqual(trades_aapl, [(10, 11, 100, 165.00)])
        # For GOOG:
        goog_buy = (20, 1678886402, "GOOG", "BUY", 50, 2500.00)
        self.assertEqual(self.engine.process_order(goog_buy), [])
        goog_sell = (21, 1678886403, "GOOG", "SELL", 50, 2495.00)
        trades_goog = self.engine.process_order(goog_sell)
        self.assertEqual(trades_goog, [(20, 21, 50, 2495.00)])
    
    def test_no_trade_when_prices_do_not_match(self):
        # Test when buy price is lower than sell price so no trade occurs.
        buy_order = (30, 1678886400, "AAPL", "BUY", 100, 160.00)
        self.assertEqual(self.engine.process_order(buy_order), [])
        sell_order = (31, 1678886401, "AAPL", "SELL", 100, 165.00)
        # Since 160.00 < 165.00, no match should occur.
        trades = self.engine.process_order(sell_order)
        self.assertEqual(trades, [])
    
    def test_invalid_order_handling(self):
        # For this test, assume that orders with invalid negative quantity should be ignored.
        # Depending on implementation, an exception could be raised.
        # Here we assume process_order returns an empty list if the order is invalid.
        invalid_order = (40, 1678886400, "AAPL", "BUY", -50, 170.00)
        try:
            trades = self.engine.process_order(invalid_order)
            # In our design, we expect no trade and no matching if the order is invalid.
            self.assertEqual(trades, [])
        except Exception as e:
            self.fail(f"process_order raised an exception for an invalid order: {str(e)}")

if __name__ == '__main__':
    unittest.main()