import json
import unittest
from dax_engine import process_order, cancel_order, clear_order_book

class TestDaxEngine(unittest.TestCase):
    def setUp(self):
        # Clear the order book before each test
        clear_order_book()

    def test_basic_limit_order_matching(self):
        # Create a sell limit order
        sell_order = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10000.00
        }
        result = process_order(sell_order)
        self.assertEqual(result, [])  # No trades yet

        # Create a matching buy limit order
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1001,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.0,
            "price": 10000.00
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 1)  # One trade should occur
        self.assertEqual(result[0]["buy_order_id"], "buy1")
        self.assertEqual(result[0]["sell_order_id"], "sell1")
        self.assertEqual(result[0]["quantity"], 1.0)
        self.assertEqual(result[0]["price"], 10000.00)
        self.assertEqual(result[0]["timestamp"], 1001)

    def test_partial_limit_order_matching(self):
        # Create a sell limit order
        sell_order = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 2.0,
            "price": 10000.00
        }
        process_order(sell_order)

        # Create a smaller buy limit order
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1001,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.0,
            "price": 10000.00
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["buy_order_id"], "buy1")
        self.assertEqual(result[0]["sell_order_id"], "sell1")
        self.assertEqual(result[0]["quantity"], 1.0)

        # Create another buy order to match the remaining sell quantity
        buy_order2 = {
            "order_id": "buy2",
            "timestamp": 1002,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.0,
            "price": 10000.00
        }
        result = process_order(buy_order2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["buy_order_id"], "buy2")
        self.assertEqual(result[0]["sell_order_id"], "sell1")
        self.assertEqual(result[0]["quantity"], 1.0)

    def test_market_order_matching(self):
        # Create a sell limit order
        sell_order = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10000.00
        }
        process_order(sell_order)

        # Create a buy market order
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1001,
            "type": "MARKET",
            "side": "BUY",
            "quantity": 1.0
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["buy_order_id"], "buy1")
        self.assertEqual(result[0]["sell_order_id"], "sell1")
        self.assertEqual(result[0]["quantity"], 1.0)
        self.assertEqual(result[0]["price"], 10000.00)

    def test_market_order_partial_fill(self):
        # Create a sell limit order
        sell_order = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 0.5,
            "price": 10000.00
        }
        process_order(sell_order)

        # Create a larger buy market order
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1001,
            "type": "MARKET",
            "side": "BUY",
            "quantity": 1.0
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["quantity"], 0.5)  # Only partial fill

    def test_price_time_priority(self):
        # Create sell limit orders at different prices
        sell_order1 = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10000.00
        }
        process_order(sell_order1)

        sell_order2 = {
            "order_id": "sell2",
            "timestamp": 1001,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10500.00
        }
        process_order(sell_order2)

        # Buy order should match with the lower price sell order first
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1002,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.5,
            "price": 11000.00
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["sell_order_id"], "sell1")  # Lower price first
        self.assertEqual(result[1]["sell_order_id"], "sell2")  # Higher price second
        self.assertEqual(result[0]["quantity"], 1.0)
        self.assertEqual(result[1]["quantity"], 0.5)

    def test_time_priority_at_same_price(self):
        # Create sell limit orders at the same price but different times
        sell_order1 = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10000.00
        }
        process_order(sell_order1)

        sell_order2 = {
            "order_id": "sell2",
            "timestamp": 1001,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10000.00
        }
        process_order(sell_order2)

        # Buy order should match with the earlier sell order first
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1002,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.5,
            "price": 10000.00
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["sell_order_id"], "sell1")  # Earlier time first
        self.assertEqual(result[1]["sell_order_id"], "sell2")  # Later time second
        self.assertEqual(result[0]["quantity"], 1.0)
        self.assertEqual(result[1]["quantity"], 0.5)

    def test_limit_price_matching(self):
        # Create a sell limit order
        sell_order = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10000.00
        }
        process_order(sell_order)

        # Buy order with higher price should match
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1001,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.0,
            "price": 10500.00
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["price"], 10000.00)  # Trade occurs at the sell price

    def test_order_cancellation(self):
        # Create a sell limit order
        sell_order = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 1.0,
            "price": 10000.00
        }
        process_order(sell_order)

        # Cancel the order
        cancel_order("sell1")

        # Try to match with a buy order
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1001,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.0,
            "price": 10000.00
        }
        result = process_order(buy_order)
        self.assertEqual(result, [])  # No trades should occur

    def test_empty_order_book_market_order(self):
        # Create a market buy order with empty order book
        buy_order = {
            "order_id": "buy1",
            "timestamp": 1000,
            "type": "MARKET",
            "side": "BUY",
            "quantity": 1.0
        }
        result = process_order(buy_order)
        self.assertEqual(result, [])  # No trades should occur

    def test_invalid_order(self):
        # Test order with negative quantity
        invalid_order = {
            "order_id": "invalid1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": -1.0,
            "price": 10000.00
        }
        result = process_order(invalid_order)
        self.assertEqual(result, [])  # Invalid order should be ignored

        # Test limit order with negative price
        invalid_order = {
            "order_id": "invalid2",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 1.0,
            "price": -100.00
        }
        result = process_order(invalid_order)
        self.assertEqual(result, [])  # Invalid order should be ignored

    def test_multiple_price_levels(self):
        # Create sell limit orders at different prices
        sell_orders = [
            {
                "order_id": f"sell{i}",
                "timestamp": 1000 + i,
                "type": "LIMIT",
                "side": "SELL",
                "quantity": 1.0,
                "price": 10000.00 + i * 100
            } for i in range(5)
        ]
        
        for order in sell_orders:
            process_order(order)

        # Buy order should match with lower prices first
        buy_order = {
            "order_id": "buy1",
            "timestamp": 2000,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 3.0,
            "price": 10500.00
        }
        
        result = process_order(buy_order)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["sell_order_id"], "sell0")  # Lowest price
        self.assertEqual(result[1]["sell_order_id"], "sell1")
        self.assertEqual(result[2]["sell_order_id"], "sell2")
        
    def test_precision_handling(self):
        # Test with 8 decimal places for quantity
        sell_order = {
            "order_id": "sell1",
            "timestamp": 1000,
            "type": "LIMIT",
            "side": "SELL",
            "quantity": 0.12345678,
            "price": 10000.00
        }
        process_order(sell_order)

        buy_order = {
            "order_id": "buy1",
            "timestamp": 1001,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 0.12345678,
            "price": 10000.00
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["quantity"], 0.12345678)

    def test_large_order_sequence(self):
        # Create 100 sell limit orders
        for i in range(100):
            sell_order = {
                "order_id": f"sell{i}",
                "timestamp": 1000 + i,
                "type": "LIMIT",
                "side": "SELL",
                "quantity": 0.1,
                "price": 10000.00 + i
            }
            process_order(sell_order)

        # Create a large buy order that matches all of them
        buy_order = {
            "order_id": "buy1",
            "timestamp": 2000,
            "type": "LIMIT",
            "side": "BUY",
            "quantity": 10.0,
            "price": 10100.00
        }
        result = process_order(buy_order)
        self.assertEqual(len(result), 100)
        
        # Check if the first match has the lowest price
        self.assertEqual(result[0]["price"], 10000.00)
        
        # Check if the last match has the highest acceptable price
        self.assertEqual(result[99]["price"], 10099.00)

if __name__ == '__main__':
    unittest.main()