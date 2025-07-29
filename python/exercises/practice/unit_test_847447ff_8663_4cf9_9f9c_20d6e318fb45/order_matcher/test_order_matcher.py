import unittest
from order_matcher.order_matcher import OrderMatchingEngine

class TestOrderMatcher(unittest.TestCase):
    def setUp(self):
        self.engine = OrderMatchingEngine()

    def test_add_buy_order_no_match(self):
        self.engine.add_order(1, "BUY", 100, 10, 1678886400)
        buy_orders, sell_orders = self.engine.get_market_depth(1)
        self.assertEqual(buy_orders, [(100, 10)])
        self.assertEqual(sell_orders, [])

    def test_add_sell_order_no_match(self):
        self.engine.add_order(1, "SELL", 100, 10, 1678886400)
        buy_orders, sell_orders = self.engine.get_market_depth(1)
        self.assertEqual(buy_orders, [])
        self.assertEqual(sell_orders, [(100, 10)])

    def test_instant_match_equal_price(self):
        self.engine.add_order(1, "BUY", 100, 10, 1678886400)
        self.engine.add_order(2, "SELL", 100, 5, 1678886401)
        
        status1 = self.engine.get_order_status(1)
        status2 = self.engine.get_order_status(2)
        self.assertEqual(status1, (5, False))
        self.assertEqual(status2, (5, False))
        
        buy_orders, sell_orders = self.engine.get_market_depth(1)
        self.assertEqual(buy_orders, [(100, 5)])
        self.assertEqual(sell_orders, [])

    def test_partial_match_buy_higher_price(self):
        self.engine.add_order(1, "BUY", 105, 10, 1678886400)
        self.engine.add_order(2, "SELL", 100, 5, 1678886401)
        
        status1 = self.engine.get_order_status(1)
        status2 = self.engine.get_order_status(2)
        self.assertEqual(status1, (5, False))
        self.assertEqual(status2, (5, False))
        
        buy_orders, sell_orders = self.engine.get_market_depth(1)
        self.assertEqual(buy_orders, [(105, 5)])
        self.assertEqual(sell_orders, [])

    def test_multiple_matches_price_priority(self):
        self.engine.add_order(1, "SELL", 95, 5, 1678886400)
        self.engine.add_order(2, "SELL", 100, 5, 1678886401)
        self.engine.add_order(3, "BUY", 100, 10, 1678886402)
        
        status1 = self.engine.get_order_status(1)
        status2 = self.engine.get_order_status(2)
        status3 = self.engine.get_order_status(3)
        self.assertEqual(status1, (5, False))
        self.assertEqual(status2, (5, False))
        self.assertEqual(status3, (10, False))
        
        buy_orders, sell_orders = self.engine.get_market_depth(2)
        self.assertEqual(buy_orders, [])
        self.assertEqual(sell_orders, [])

    def test_time_priority_same_price(self):
        self.engine.add_order(1, "BUY", 100, 5, 1678886400)
        self.engine.add_order(2, "BUY", 100, 5, 1678886401)
        self.engine.add_order(3, "SELL", 100, 5, 1678886402)
        
        status1 = self.engine.get_order_status(1)
        status2 = self.engine.get_order_status(2)
        status3 = self.engine.get_order_status(3)
        self.assertEqual(status1, (5, False))
        self.assertEqual(status2, (0, False))
        self.assertEqual(status3, (5, False))

    def test_cancel_order(self):
        self.engine.add_order(1, "BUY", 100, 10, 1678886400)
        self.assertTrue(self.engine.cancel_order(1))
        
        status = self.engine.get_order_status(1)
        self.assertEqual(status, (0, True))
        
        buy_orders, _ = self.engine.get_market_depth(1)
        self.assertEqual(buy_orders, [])

    def test_cancel_partially_filled_order(self):
        self.engine.add_order(1, "BUY", 100, 10, 1678886400)
        self.engine.add_order(2, "SELL", 100, 5, 1678886401)
        self.assertTrue(self.engine.cancel_order(1))
        
        status = self.engine.get_order_status(1)
        self.assertEqual(status, (5, True))

    def test_cancel_nonexistent_order(self):
        self.assertFalse(self.engine.cancel_order(999))

    def test_get_market_depth_multiple_levels(self):
        self.engine.add_order(1, "BUY", 100, 5, 1678886400)
        self.engine.add_order(2, "BUY", 99, 3, 1678886401)
        self.engine.add_order(3, "SELL", 101, 2, 1678886402)
        self.engine.add_order(4, "SELL", 102, 4, 1678886403)
        
        buy_orders, sell_orders = self.engine.get_market_depth(2)
        self.assertEqual(buy_orders, [(100, 5), (99, 3)])
        self.assertEqual(sell_orders, [(101, 2), (102, 4)])

    def test_zero_quantity_order(self):
        with self.assertRaises(ValueError):
            self.engine.add_order(1, "BUY", 100, 0, 1678886400)

    def test_duplicate_order_id(self):
        self.engine.add_order(1, "BUY", 100, 10, 1678886400)
        with self.assertRaises(ValueError):
            self.engine.add_order(1, "SELL", 95, 5, 1678886401)

if __name__ == '__main__':
    unittest.main()