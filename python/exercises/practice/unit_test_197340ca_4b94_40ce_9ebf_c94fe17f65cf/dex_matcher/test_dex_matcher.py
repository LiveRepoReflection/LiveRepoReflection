import unittest
from datetime import datetime

class DexMatcherTest(unittest.TestCase):
    def setUp(self):
        from dex_matcher import DEXMatcher
        self.matcher = DEXMatcher()

    def test_empty_order_book(self):
        self.assertEqual(self.matcher.get_order_book(), {"buy": {}, "sell": {}})

    def test_single_buy_order(self):
        order = {
            "type": "order",
            "order_id": "order1",
            "timestamp": 1678886400000,
            "price": 1000000000,
            "quantity": 10,
            "side": "buy"
        }
        trades = self.matcher.process_message(order)
        self.assertEqual(len(trades), 0)
        book = self.matcher.get_order_book()
        self.assertEqual(len(book["buy"]), 1)
        self.assertEqual(len(book["sell"]), 0)

    def test_matching_orders(self):
        buy_order = {
            "type": "order",
            "order_id": "order1",
            "timestamp": 1678886400000,
            "price": 1000000000,
            "quantity": 10,
            "side": "buy"
        }
        sell_order = {
            "type": "order",
            "order_id": "order2",
            "timestamp": 1678886400001,
            "price": 1000000000,
            "quantity": 5,
            "side": "sell"
        }
        
        self.matcher.process_message(buy_order)
        trades = self.matcher.process_message(sell_order)
        
        self.assertEqual(len(trades), 1)
        trade = trades[0]
        self.assertEqual(trade["taker_order_id"], "order2")
        self.assertEqual(trade["maker_order_id"], "order1")
        self.assertEqual(trade["price"], 1000000000)
        self.assertEqual(trade["quantity"], 5)
        self.assertEqual(trade["timestamp"], 1678886400001)

    def test_order_cancellation(self):
        order = {
            "type": "order",
            "order_id": "order1",
            "timestamp": 1678886400000,
            "price": 1000000000,
            "quantity": 10,
            "side": "buy"
        }
        cancel = {
            "type": "cancel",
            "order_id": "order1",
            "timestamp": 1678886400002
        }
        
        self.matcher.process_message(order)
        self.matcher.process_message(cancel)
        book = self.matcher.get_order_book()
        self.assertEqual(len(book["buy"]), 0)

    def test_multiple_price_levels(self):
        orders = [
            {
                "type": "order",
                "order_id": "buy1",
                "timestamp": 1678886400000,
                "price": 1000000000,
                "quantity": 5,
                "side": "buy"
            },
            {
                "type": "order",
                "order_id": "buy2",
                "timestamp": 1678886400001,
                "price": 1100000000,
                "quantity": 3,
                "side": "buy"
            },
            {
                "type": "order",
                "order_id": "sell1",
                "timestamp": 1678886400002,
                "price": 1000000000,
                "quantity": 8,
                "side": "sell"
            }
        ]
        
        for order in orders[:2]:
            self.matcher.process_message(order)
            
        trades = self.matcher.process_message(orders[2])
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[0]["price"], 1100000000)
        self.assertEqual(trades[0]["quantity"], 3)
        self.assertEqual(trades[1]["price"], 1000000000)
        self.assertEqual(trades[1]["quantity"], 5)

    def test_zero_quantity_order(self):
        order = {
            "type": "order",
            "order_id": "order1",
            "timestamp": 1678886400000,
            "price": 1000000000,
            "quantity": 0,
            "side": "buy"
        }
        trades = self.matcher.process_message(order)
        self.assertEqual(len(trades), 0)
        book = self.matcher.get_order_book()
        self.assertEqual(len(book["buy"]), 0)

    def test_non_existent_order_cancellation(self):
        cancel = {
            "type": "cancel",
            "order_id": "nonexistent",
            "timestamp": 1678886400000
        }
        result = self.matcher.process_message(cancel)
        self.assertIsNone(result)

    def test_partial_fills(self):
        orders = [
            {
                "type": "order",
                "order_id": "sell1",
                "timestamp": 1678886400000,
                "price": 1000000000,
                "quantity": 10,
                "side": "sell"
            },
            {
                "type": "order",
                "order_id": "buy1",
                "timestamp": 1678886400001,
                "price": 1000000000,
                "quantity": 4,
                "side": "buy"
            },
            {
                "type": "order",
                "order_id": "buy2",
                "timestamp": 1678886400002,
                "price": 1000000000,
                "quantity": 3,
                "side": "buy"
            }
        ]
        
        self.matcher.process_message(orders[0])
        trades1 = self.matcher.process_message(orders[1])
        trades2 = self.matcher.process_message(orders[2])
        
        self.assertEqual(len(trades1), 1)
        self.assertEqual(trades1[0]["quantity"], 4)
        self.assertEqual(len(trades2), 1)
        self.assertEqual(trades2[0]["quantity"], 3)
        
        book = self.matcher.get_order_book()
        self.assertEqual(book["sell"][1000000000][0]["quantity"], 3)

    def test_time_priority(self):
        orders = [
            {
                "type": "order",
                "order_id": "buy1",
                "timestamp": 1678886400000,
                "price": 1000000000,
                "quantity": 5,
                "side": "buy"
            },
            {
                "type": "order",
                "order_id": "buy2",
                "timestamp": 1678886400001,
                "price": 1000000000,
                "quantity": 5,
                "side": "buy"
            },
            {
                "type": "order",
                "order_id": "sell1",
                "timestamp": 1678886400002,
                "price": 1000000000,
                "quantity": 7,
                "side": "sell"
            }
        ]
        
        for order in orders[:2]:
            self.matcher.process_message(order)
            
        trades = self.matcher.process_message(orders[2])
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[0]["maker_order_id"], "buy1")
        self.assertEqual(trades[1]["maker_order_id"], "buy2")

if __name__ == '__main__':
    unittest.main()