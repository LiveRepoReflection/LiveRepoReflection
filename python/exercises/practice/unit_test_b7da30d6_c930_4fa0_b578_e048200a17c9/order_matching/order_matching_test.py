import unittest
from order_matching import MatchingEngine

class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MatchingEngine()

    def test_add_single_buy_order(self):
        order = ("order1", "BUY", 100, 10)
        self.engine.add_order(order)
        buy_book, sell_book = self.engine.get_order_book()
        self.assertEqual(len(buy_book), 1)
        self.assertEqual(len(sell_book), 0)
        self.assertEqual(buy_book[0], order)

    def test_add_single_sell_order(self):
        order = ("order1", "SELL", 100, 10)
        self.engine.add_order(order)
        buy_book, sell_book = self.engine.get_order_book()
        self.assertEqual(len(buy_book), 0)
        self.assertEqual(len(sell_book), 1)
        self.assertEqual(sell_book[0], order)

    def test_match_exact_price_and_quantity(self):
        self.engine.add_order(("order1", "BUY", 100, 10))
        self.engine.add_order(("order2", "SELL", 100, 10))
        buy_book, sell_book = self.engine.get_order_book()
        self.assertEqual(len(buy_book), 0)
        self.assertEqual(len(sell_book), 0)
        trades = self.engine.get_trades()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0], ("order1", "order2", 100, 10))

    def test_match_better_price(self):
        self.engine.add_order(("order1", "BUY", 110, 10))
        self.engine.add_order(("order2", "SELL", 100, 10))
        trades = self.engine.get_trades()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0], ("order1", "order2", 100, 10))

    def test_partial_fill(self):
        self.engine.add_order(("order1", "BUY", 100, 10))
        self.engine.add_order(("order2", "SELL", 100, 5))
        buy_book, sell_book = self.engine.get_order_book()
        self.assertEqual(len(buy_book), 1)
        self.assertEqual(len(sell_book), 0)
        self.assertEqual(buy_book[0], ("order1", "BUY", 100, 5))

    def test_price_time_priority(self):
        self.engine.add_order(("order1", "BUY", 100, 10))
        self.engine.add_order(("order2", "BUY", 110, 10))
        self.engine.add_order(("order3", "BUY", 100, 10))
        buy_book, _ = self.engine.get_order_book()
        self.assertEqual(buy_book[0], ("order2", "BUY", 110, 10))
        self.assertEqual(buy_book[1], ("order1", "BUY", 100, 10))
        self.assertEqual(buy_book[2], ("order3", "BUY", 100, 10))

    def test_cancel_order(self):
        self.engine.add_order(("order1", "BUY", 100, 10))
        self.engine.cancel_order("order1")
        buy_book, _ = self.engine.get_order_book()
        self.assertEqual(len(buy_book), 0)

    def test_cancel_nonexistent_order(self):
        with self.assertRaises(ValueError):
            self.engine.cancel_order("nonexistent")

    def test_multiple_matches(self):
        self.engine.add_order(("order1", "BUY", 100, 20))
        self.engine.add_order(("order2", "SELL", 95, 5))
        self.engine.add_order(("order3", "SELL", 98, 10))
        self.engine.add_order(("order4", "SELL", 100, 5))
        
        trades = self.engine.get_trades()
        self.assertEqual(len(trades), 3)
        buy_book, sell_book = self.engine.get_order_book()
        self.assertEqual(len(buy_book), 0)
        self.assertEqual(len(sell_book), 0)

    def test_invalid_order_type(self):
        with self.assertRaises(ValueError):
            self.engine.add_order(("order1", "INVALID", 100, 10))

    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            self.engine.add_order(("order1", "BUY", -100, 10))

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.engine.add_order(("order1", "BUY", 100, 0))

    def test_duplicate_order_id(self):
        self.engine.add_order(("order1", "BUY", 100, 10))
        with self.assertRaises(ValueError):
            self.engine.add_order(("order1", "SELL", 100, 10))

if __name__ == '__main__':
    unittest.main()