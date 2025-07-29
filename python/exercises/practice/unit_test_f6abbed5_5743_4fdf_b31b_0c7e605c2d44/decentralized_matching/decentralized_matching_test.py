import unittest
import time
from decentralized_matching import MatchingEngine

class DecentralizedMatchingTest(unittest.TestCase):
    def setUp(self):
        # Initialize a new matching engine before each test case
        self.engine = MatchingEngine()
        # For test consistency, we'll use a fixed timestamp base
        self.base_timestamp = 1678886400

    def submit_orders(self, orders):
        for order in orders:
            self.engine.submit_order(order)

    def test_no_orders(self):
        # No orders submitted: the trade list should be empty.
        self.assertEqual(self.engine.get_trade_records(), [])

    def test_single_match_full_fill(self):
        # Create a buy order and a sell order that exactly match.
        orders = [
            {"order_id": "B1", "user_id": "User1", "order_type": "BUY", "price": 10.0, "quantity": 1.0, "timestamp": self.base_timestamp},
            {"order_id": "S1", "user_id": "User2", "order_type": "SELL", "price": 9.5, "quantity": 1.0, "timestamp": self.base_timestamp + 1}
        ]
        self.submit_orders(orders)
        trades = self.engine.get_trade_records()
        self.assertEqual(len(trades), 1)

        trade = trades[0]
        # When buy price > sell price, trade price should be sell order's price.
        self.assertEqual(trade["price"], 9.5)
        self.assertEqual(trade["quantity"], 1.0)
        self.assertEqual(trade["buy_order_id"], "B1")
        self.assertEqual(trade["sell_order_id"], "S1")

    def test_single_match_partial_fill(self):
        # Create a buy order that is larger than the sell order quantity.
        orders = [
            {"order_id": "B1", "user_id": "User1", "order_type": "BUY", "price": 10.0, "quantity": 2.0, "timestamp": self.base_timestamp},
            {"order_id": "S1", "user_id": "User2", "order_type": "SELL", "price": 9.5, "quantity": 1.0, "timestamp": self.base_timestamp + 1}
        ]
        self.submit_orders(orders)
        trades = self.engine.get_trade_records()
        self.assertEqual(len(trades), 1)
        trade = trades[0]
        self.assertEqual(trade["price"], 9.5)
        self.assertEqual(trade["quantity"], 1.0)
        # The remaining part of the buy order should still be in the order book.
        remaining_buy = self.engine.get_order_book("BUY")
        self.assertEqual(len(remaining_buy), 1)
        self.assertAlmostEqual(remaining_buy[0]["quantity"], 1.0, places=6)

    def test_multiple_matches_with_priority(self):
        # Testing multiple orders to ensure correct matching order.
        orders = [
            {"order_id": "B1", "user_id": "User1", "order_type": "BUY", "price": 10.0, "quantity": 1.0, "timestamp": self.base_timestamp},
            {"order_id": "B2", "user_id": "User2", "order_type": "BUY", "price": 10.2, "quantity": 0.5, "timestamp": self.base_timestamp + 1},
            {"order_id": "S1", "user_id": "User3", "order_type": "SELL", "price": 9.8, "quantity": 0.3, "timestamp": self.base_timestamp + 2},
            {"order_id": "S2", "user_id": "User4", "order_type": "SELL", "price": 10.0, "quantity": 0.8, "timestamp": self.base_timestamp + 3},
        ]
        self.submit_orders(orders)
        trades = self.engine.get_trade_records()
        # There should be two trades executed: first trade with highest buy priority (B2) matching S1,
        # then subsequent matching of remaining sell quantities with B1 or leftover from B2.
        self.assertTrue(len(trades) >= 2)
        # Verify trade details for each trade
        trade1 = trades[0]
        if trade1["buy_order_id"] == "B2":
            self.assertEqual(trade1["sell_order_id"], "S1")
            self.assertEqual(trade1["price"], 9.8)
            self.assertEqual(trade1["quantity"], 0.3)
        else:
            self.fail("First trade did not involve the highest bid order B2 as expected.")

        # Verify that subsequent trade(s) cover the remaining quantity.
        remaining_sell = self.engine.get_order_book("SELL")
        # Depending on matching, the remaining sell orders should have the expected quantities.
        # If S1 is fully filled, S2 might be partially filled.
        for order in remaining_sell:
            self.assertGreater(order["quantity"], 0)

    def test_order_book_sorting_buy(self):
        # Submit multiple buy orders with different prices and timestamps
        orders = [
            {"order_id": "B1", "user_id": "User1", "order_type": "BUY", "price": 9.8, "quantity": 1.0, "timestamp": self.base_timestamp},
            {"order_id": "B2", "user_id": "User2", "order_type": "BUY", "price": 10.0, "quantity": 2.0, "timestamp": self.base_timestamp + 2},
            {"order_id": "B3", "user_id": "User3", "order_type": "BUY", "price": 10.0, "quantity": 1.5, "timestamp": self.base_timestamp + 1}
        ]
        self.submit_orders(orders)
        buy_book = self.engine.get_order_book("BUY")
        # Expect buy orders sorted descending by price, then ascending by timestamp
        # The order for price=10.0 should have B3 before B2 as its timestamp is earlier.
        self.assertEqual(buy_book[0]["order_id"], "B3")
        self.assertEqual(buy_book[1]["order_id"], "B2")
        self.assertEqual(buy_book[2]["order_id"], "B1")

    def test_order_book_sorting_sell(self):
        # Submit multiple sell orders with different prices and timestamps
        orders = [
            {"order_id": "S1", "user_id": "User1", "order_type": "SELL", "price": 10.2, "quantity": 1.0, "timestamp": self.base_timestamp},
            {"order_id": "S2", "user_id": "User2", "order_type": "SELL", "price": 10.0, "quantity": 2.0, "timestamp": self.base_timestamp + 2},
            {"order_id": "S3", "user_id": "User3", "order_type": "SELL", "price": 10.0, "quantity": 1.5, "timestamp": self.base_timestamp + 1}
        ]
        self.submit_orders(orders)
        sell_book = self.engine.get_order_book("SELL")
        # Expect sell orders sorted ascending by price, then ascending by timestamp
        # The orders with price 10.0 should list S3 before S2.
        self.assertEqual(sell_book[0]["order_id"], "S3")
        self.assertEqual(sell_book[1]["order_id"], "S2")
        self.assertEqual(sell_book[2]["order_id"], "S1")

    def test_trade_price_determination(self):
        # Test when the buy price equals the sell price.
        orders = [
            {"order_id": "B1", "user_id": "User1", "order_type": "BUY", "price": 10.0, "quantity": 1.0, "timestamp": self.base_timestamp},
            {"order_id": "S1", "user_id": "User2", "order_type": "SELL", "price": 10.0, "quantity": 1.0, "timestamp": self.base_timestamp + 1}
        ]
        self.submit_orders(orders)
        trades = self.engine.get_trade_records()
        self.assertEqual(len(trades), 1)
        trade = trades[0]
        # When prices are equal, trade price should be the buy order's price (as per rules).
        self.assertEqual(trade["price"], 10.0)

    def test_concurrent_order_submissions(self):
        # Simulate concurrent order submissions by submitting orders out of timestamp order.
        orders = [
            {"order_id": "B1", "user_id": "User1", "order_type": "BUY", "price": 10.0, "quantity": 1.0, "timestamp": self.base_timestamp + 5},
            {"order_id": "S1", "user_id": "User2", "order_type": "SELL", "price": 9.5, "quantity": 0.5, "timestamp": self.base_timestamp + 1},
            {"order_id": "B2", "user_id": "User3", "order_type": "BUY", "price": 10.2, "quantity": 0.5, "timestamp": self.base_timestamp + 2},
            {"order_id": "S2", "user_id": "User4", "order_type": "SELL", "price": 9.8, "quantity": 1.0, "timestamp": self.base_timestamp + 3},
            {"order_id": "B3", "user_id": "User5", "order_type": "BUY", "price": 10.1, "quantity": 0.7, "timestamp": self.base_timestamp + 4}
        ]
        # Submitting orders in a shuffled order to simulate concurrency
        for order in [orders[1], orders[3], orders[0], orders[2], orders[4]]:
            self.engine.submit_order(order)
        trades = self.engine.get_trade_records()
        # Check that trades have been executed and trade records are non-empty.
        self.assertTrue(len(trades) > 0)

    def test_trade_immutability(self):
        # Test that once trade records are generated, they cannot be altered by subsequent operations.
        orders = [
            {"order_id": "B1", "user_id": "User1", "order_type": "BUY", "price": 10.5, "quantity": 1.0, "timestamp": self.base_timestamp},
            {"order_id": "S1", "user_id": "User2", "order_type": "SELL", "price": 10.0, "quantity": 1.0, "timestamp": self.base_timestamp + 1}
        ]
        self.submit_orders(orders)
        trades_before = self.engine.get_trade_records()
        # Add an order that will not match and verify the trades remain unchanged.
        self.engine.submit_order({
            "order_id": "B2", "user_id": "User3", "order_type": "BUY", "price": 9.0, "quantity": 1.0, "timestamp": self.base_timestamp + 2
        })
        trades_after = self.engine.get_trade_records()
        self.assertEqual(trades_before, trades_after)

if __name__ == '__main__':
    unittest.main()