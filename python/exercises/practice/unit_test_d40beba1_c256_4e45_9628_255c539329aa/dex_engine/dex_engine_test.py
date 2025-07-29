import unittest
from dex_engine.dex_engine import OrderMatchingEngine

class DexEngineTest(unittest.TestCase):
    def setUp(self):
        # Initialize the order matching engine instance before each test.
        self.engine = OrderMatchingEngine()

    def test_no_match(self):
        # Test that a solitary order does not produce any trades.
        event = (1, "B1", "BID", 10.0, 5, False)
        trades = self.engine.process_order(event)
        self.assertEqual(trades, [])

    def test_single_match(self):
        # Place a bid order and then an ask order that should trigger a match.
        bid_event = (1, "B1", "BID", 10.0, 5, False)
        ask_event = (2, "A1", "ASK", 9.5, 3, False)
        self.engine.process_order(bid_event)
        trades = self.engine.process_order(ask_event)
        # Expect a trade with the ask order as taker, bid order as maker.
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0], ("A1", "B1", 10.0, 3))

    def test_partial_fill(self):
        # Test partial fills: bid order is partially filled by successive ask orders.
        bid_event = (1, "B1", "BID", 10.0, 5, False)
        ask_event1 = (2, "A1", "ASK", 9.5, 3, False)
        ask_event2 = (3, "A2", "ASK", 9.0, 4, False)
        self.engine.process_order(bid_event)
        trades1 = self.engine.process_order(ask_event1)
        self.assertEqual(len(trades1), 1)
        self.assertEqual(trades1[0], ("A1", "B1", 10.0, 3))
        trades2 = self.engine.process_order(ask_event2)
        # Only 2 units remain in the bid order; hence, expect a partial fill.
        self.assertEqual(len(trades2), 1)
        self.assertEqual(trades2[0], ("A2", "B1", 10.0, 2))

    def test_priority_by_timestamp(self):
        # When multiple ask orders have the same price, the earliest order should be matched first.
        bid_event = (1, "B1", "BID", 10.0, 5, False)
        ask_event1 = (2, "A1", "ASK", 9.5, 3, False)  # Earlier ask order
        ask_event2 = (3, "A2", "ASK", 9.5, 3, False)  # Later ask order
        self.engine.process_order(bid_event)
        trades1 = self.engine.process_order(ask_event1)
        self.assertEqual(len(trades1), 1)
        self.assertEqual(trades1[0], ("A1", "B1", 10.0, 3))
        trades2 = self.engine.process_order(ask_event2)
        # Remaining bid order quantity should match partially with the second ask order.
        self.assertEqual(len(trades2), 1)
        self.assertEqual(trades2[0], ("A2", "B1", 10.0, 2))

    def test_cancellation(self):
        # Test that an order cancellation removes the order from the order book.
        bid_event = (1, "B1", "BID", 10.0, 5, False)
        cancel_event = (2, "B1", "BID", 0, 0, True)
        ask_event = (3, "A1", "ASK", 9.5, 3, False)
        self.engine.process_order(bid_event)
        cancel_trades = self.engine.process_order(cancel_event)
        self.assertEqual(cancel_trades, [])
        trades = self.engine.process_order(ask_event)
        # Since the bid is cancelled, no match should occur.
        self.assertEqual(trades, [])

    def test_multiple_matches(self):
        # Test multiple matches across different orders.
        bid_event1 = (1, "B1", "BID", 10.0, 3, False)
        bid_event2 = (2, "B2", "BID", 9.8, 2, False)
        ask_event1 = (3, "A1", "ASK", 9.5, 2, False)
        ask_event2 = (4, "A2", "ASK", 9.7, 3, False)
        self.engine.process_order(bid_event1)
        self.engine.process_order(bid_event2)
        trades1 = self.engine.process_order(ask_event1)
        self.assertEqual(len(trades1), 1)
        self.assertEqual(trades1[0], ("A1", "B1", 10.0, 2))
        trades2 = self.engine.process_order(ask_event2)
        # The remaining bid order B1 has 1 unit and bid B2 has 2 units.
        self.assertEqual(len(trades2), 2)
        self.assertEqual(trades2[0], ("A2", "B1", 10.0, 1))
        self.assertEqual(trades2[1], ("A2", "B2", 9.8, 2))

    def test_floating_point_tolerance(self):
        # Ensure slight floating point imprecisions in price comparison do not cause matching failures.
        bid_event = (1, "B1", "BID", 10.000001, 5, False)
        ask_event = (2, "A1", "ASK", 10.000000, 5, False)
        self.engine.process_order(bid_event)
        trades = self.engine.process_order(ask_event)
        self.assertEqual(len(trades), 1)
        self.assertAlmostEqual(trades[0][2], 10.000001, delta=1e-6)
        self.assertEqual(trades[0][3], 5)

if __name__ == '__main__':
    unittest.main()