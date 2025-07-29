import unittest
from algo_exchange import AlgorithmicStockExchange

class TestAlgorithmicStockExchange(unittest.TestCase):
    def setUp(self):
        self.exchange = AlgorithmicStockExchange()

    def test_no_orders(self):
        # When no orders have been added, top-of-book should return (None, None)
        self.assertEqual(self.exchange.get_top_of_book("AAPL"), (None, None))

    def test_single_buy_order(self):
        # Add a single BUY order and verify that best bid is updated and ask remains None.
        self.exchange.add_order(1, 1000, "AAPL", "BUY", 150, 100)
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (150, None))

    def test_single_sell_order(self):
        # Add a single SELL order and verify that best ask is updated and bid remains None.
        self.exchange.add_order(2, 1000, "AAPL", "SELL", 155, 50)
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (None, 155))

    def test_full_match_buy_and_sell(self):
        # Test a full match where a BUY order is completely filled by a matching SELL order.
        self.exchange.add_order(1, 1000, "AAPL", "BUY", 150, 100)
        self.exchange.add_order(2, 1001, "AAPL", "SELL", 150, 100)
        # After complete matching, both sides should be empty.
        self.assertEqual(self.exchange.get_top_of_book("AAPL"), (None, None))

    def test_partial_match(self):
        # Test scenario where a BUY order is partially filled by a larger SELL order.
        self.exchange.add_order(1, 1000, "AAPL", "BUY", 150, 100)
        self.exchange.add_order(2, 1001, "AAPL", "SELL", 150, 150)
        # BUY order is fully matched and removed, SELL order remains with 50 shares.
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (None, 150))

    def test_multiple_matches(self):
        # Add two BUY orders at different prices.
        self.exchange.add_order(1, 1000, "AAPL", "BUY", 151, 100)
        self.exchange.add_order(2, 1001, "AAPL", "BUY", 150, 100)
        # Add a SELL order that can match both BUY orders.
        self.exchange.add_order(3, 1002, "AAPL", "SELL", 150, 150)
        # Matching should occur as follows:
        # Order 1 (BUY at 151, qty 100) fully matched, leaving SELL order with 50 shares.
        # Order 2 (BUY at 150, qty 100) partially matched (50 shares), remaining qty 50.
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (150, None))

    def test_cancel_order(self):
        # Add a BUY and a SELL order, then cancel each and verify top-of-book updates accordingly.
        self.exchange.add_order(1, 1000, "AAPL", "BUY", 150, 100)
        self.exchange.add_order(2, 1001, "AAPL", "SELL", 155, 50)
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (150, 155))
        # Cancel the SELL order.
        self.exchange.cancel_order(2, 1002)
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (150, None))
        # Cancel the BUY order.
        self.exchange.cancel_order(1, 1003)
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (None, None))

    def test_consecutive_operations(self):
        # Simulate a complex scenario with multiple orders, partial fills, and cancellations.
        self.exchange.add_order(1, 1000, "AAPL", "BUY", 152, 200)  # BUY 200 @152
        self.exchange.add_order(2, 1001, "AAPL", "BUY", 150, 100)  # BUY 100 @150
        self.exchange.add_order(3, 1002, "AAPL", "SELL", 153, 150) # SELL 150 @153 (no match)
        # Top-of-book should be best bid 152 and best ask 153.
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (152, 153))
        
        # Add SELL order that matches with the best bid.
        self.exchange.add_order(4, 1003, "AAPL", "SELL", 152, 250) # SELL 250 @152
        # Matching: Order 1 (BUY 200 @152) is fully filled, leaving order 4 with 50 shares.
        # Order 2 remains completely unmatched.
        top = self.exchange.get_top_of_book("AAPL")
        # Now, best bid is order 2 with price 150 and best ask is the lowest price from remaining SELL orders: order 4 at 152.
        self.assertEqual(top, (150, 152))
        
        # Cancel the SELL order at 153.
        self.exchange.cancel_order(3, 1004)
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (150, 152))
        
        # Cancel the remaining SELL order (order 4).
        self.exchange.cancel_order(4, 1005)
        top = self.exchange.get_top_of_book("AAPL")
        self.assertEqual(top, (150, None))

if __name__ == '__main__':
    unittest.main()