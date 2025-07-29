import unittest
from datetime import datetime, timedelta

class TestDASE(unittest.TestCase):
    def setUp(self):
        from dase_engine import DASE
        self.dase = DASE()
        self.base_timestamp = int(datetime(2024, 1, 1).timestamp())

    def test_basic_order_submission(self):
        order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "BUY",
            "price": 1500000,  # $150.00
            "quantity": 10,
            "timestamp": self.base_timestamp
        }
        self.assertTrue(self.dase.submit_order(order))
        order_book = self.dase.get_order_book("AAPL")
        self.assertEqual(len(order_book["bids"]), 1)
        self.assertEqual(len(order_book["asks"]), 0)

    def test_order_matching_exact(self):
        # Submit sell order first
        sell_order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "SELL",
            "price": 1500000,  # $150.00
            "quantity": 10,
            "timestamp": self.base_timestamp
        }
        self.dase.submit_order(sell_order)

        # Submit matching buy order
        buy_order = {
            "order_id": "2",
            "user_id": "user2",
            "stock_symbol": "AAPL",
            "order_type": "BUY",
            "price": 1500000,  # $150.00
            "quantity": 10,
            "timestamp": self.base_timestamp + 1
        }
        self.dase.submit_order(buy_order)

        # Check order book is empty (full match)
        order_book = self.dase.get_order_book("AAPL")
        self.assertEqual(len(order_book["bids"]), 0)
        self.assertEqual(len(order_book["asks"]), 0)

        # Check trades
        trades = self.dase.get_trades("AAPL")
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["quantity"], 10)
        self.assertEqual(trades[0]["price"], 1500000)

    def test_partial_fill(self):
        # Submit sell order for 10 shares
        sell_order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "SELL",
            "price": 1500000,
            "quantity": 10,
            "timestamp": self.base_timestamp
        }
        self.dase.submit_order(sell_order)

        # Submit buy order for 6 shares
        buy_order = {
            "order_id": "2",
            "user_id": "user2",
            "stock_symbol": "AAPL",
            "order_type": "BUY",
            "price": 1500000,
            "quantity": 6,
            "timestamp": self.base_timestamp + 1
        }
        self.dase.submit_order(buy_order)

        # Check order book (should have 4 shares remaining to sell)
        order_book = self.dase.get_order_book("AAPL")
        self.assertEqual(len(order_book["asks"]), 1)
        self.assertEqual(order_book["asks"][0]["quantity"], 4)

    def test_price_time_priority(self):
        # Submit multiple buy orders at different prices and times
        orders = [
            {
                "order_id": "1",
                "user_id": "user1",
                "stock_symbol": "AAPL",
                "order_type": "BUY",
                "price": 1500000,
                "quantity": 10,
                "timestamp": self.base_timestamp
            },
            {
                "order_id": "2",
                "user_id": "user2",
                "stock_symbol": "AAPL",
                "order_type": "BUY",
                "price": 1510000,
                "quantity": 10,
                "timestamp": self.base_timestamp + 2
            },
            {
                "order_id": "3",
                "user_id": "user3",
                "stock_symbol": "AAPL",
                "order_type": "BUY",
                "price": 1510000,
                "quantity": 10,
                "timestamp": self.base_timestamp + 1
            }
        ]

        for order in orders:
            self.dase.submit_order(order)

        order_book = self.dase.get_order_book("AAPL")
        self.assertEqual(len(order_book["bids"]), 3)
        # Check price priority
        self.assertEqual(order_book["bids"][0]["price"], 1510000)
        self.assertEqual(order_book["bids"][1]["price"], 1510000)
        # Check time priority for same price
        self.assertEqual(order_book["bids"][0]["order_id"], "3")
        self.assertEqual(order_book["bids"][1]["order_id"], "2")

    def test_order_cancellation(self):
        order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "BUY",
            "price": 1500000,
            "quantity": 10,
            "timestamp": self.base_timestamp
        }
        self.dase.submit_order(order)
        self.assertTrue(self.dase.cancel_order("1"))
        order_book = self.dase.get_order_book("AAPL")
        self.assertEqual(len(order_book["bids"]), 0)

    def test_last_traded_price(self):
        # Submit matching orders
        sell_order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "SELL",
            "price": 1500000,
            "quantity": 10,
            "timestamp": self.base_timestamp
        }
        buy_order = {
            "order_id": "2",
            "user_id": "user2",
            "stock_symbol": "AAPL",
            "order_type": "BUY",
            "price": 1500000,
            "quantity": 10,
            "timestamp": self.base_timestamp + 1
        }

        self.assertIsNone(self.dase.get_last_traded_price("AAPL"))
        
        self.dase.submit_order(sell_order)
        self.dase.submit_order(buy_order)

        self.assertEqual(self.dase.get_last_traded_price("AAPL"), 1500000)

    def test_invalid_orders(self):
        # Test missing fields
        invalid_order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "BUY",
            # missing price
            "quantity": 10,
            "timestamp": self.base_timestamp
        }
        self.assertFalse(self.dase.submit_order(invalid_order))

        # Test invalid order type
        invalid_order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "INVALID",
            "price": 1500000,
            "quantity": 10,
            "timestamp": self.base_timestamp
        }
        self.assertFalse(self.dase.submit_order(invalid_order))

        # Test negative quantity
        invalid_order = {
            "order_id": "1",
            "user_id": "user1",
            "stock_symbol": "AAPL",
            "order_type": "BUY",
            "price": 1500000,
            "quantity": -10,
            "timestamp": self.base_timestamp
        }
        self.assertFalse(self.dase.submit_order(invalid_order))

    def test_multiple_stocks(self):
        # Submit orders for different stocks
        orders = [
            {
                "order_id": "1",
                "user_id": "user1",
                "stock_symbol": "AAPL",
                "order_type": "BUY",
                "price": 1500000,
                "quantity": 10,
                "timestamp": self.base_timestamp
            },
            {
                "order_id": "2",
                "user_id": "user2",
                "stock_symbol": "GOOGL",
                "order_type": "BUY",
                "price": 2500000,
                "quantity": 5,
                "timestamp": self.base_timestamp
            }
        ]

        for order in orders:
            self.dase.submit_order(order)

        aapl_book = self.dase.get_order_book("AAPL")
        googl_book = self.dase.get_order_book("GOOGL")

        self.assertEqual(len(aapl_book["bids"]), 1)
        self.assertEqual(len(googl_book["bids"]), 1)
        self.assertEqual(aapl_book["bids"][0]["price"], 1500000)
        self.assertEqual(googl_book["bids"][0]["price"], 2500000)

if __name__ == '__main__':
    unittest.main()