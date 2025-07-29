import unittest
from enum import Enum
from dex_orderbook import OrderBook, Order, Side

class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.order_book = OrderBook()

    def test_empty_orderbook(self):
        # Test operations on an empty order book
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(len(self.order_book.asks), 0)
        
        # Test market order on empty book
        remaining = self.order_book.execute_market_order(Side.BID, 100)
        self.assertEqual(remaining, 100)
        
        # Test canceling non-existent order
        with self.assertRaises(Exception):
            self.order_book.cancel_order(999)

    def test_add_limit_order_no_match(self):
        # Add bid and ask orders that don't match
        bid_order = Order(1, 101, Side.BID, 95, 10, 1000)
        ask_order = Order(2, 102, Side.ASK, 100, 10, 1001)
        
        self.order_book.add_limit_order(bid_order)
        self.order_book.add_limit_order(ask_order)
        
        # Check if orders are properly added
        self.assertEqual(len(self.order_book.bids), 1)
        self.assertEqual(len(self.order_book.asks), 1)
        
        # Check if orders are in the correct order
        self.assertEqual(self.order_book.bids[0].order_id, 1)
        self.assertEqual(self.order_book.asks[0].order_id, 2)

    def test_add_limit_order_with_match(self):
        # Add ask order first
        ask_order = Order(1, 101, Side.ASK, 100, 10, 1000)
        self.order_book.add_limit_order(ask_order)
        
        # Add matching bid order
        bid_order = Order(2, 102, Side.BID, 100, 5, 1001)
        self.order_book.add_limit_order(bid_order)
        
        # The bid should be fully matched and removed
        self.assertEqual(len(self.order_book.bids), 0)
        
        # The ask should be partially filled and remain in the book
        self.assertEqual(len(self.order_book.asks), 1)
        self.assertEqual(self.order_book.asks[0].quantity, 5)
        
        # Add another matching bid order that fully consumes the ask
        bid_order2 = Order(3, 103, Side.BID, 100, 5, 1002)
        self.order_book.add_limit_order(bid_order2)
        
        # Both orders should be fully matched and removed
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(len(self.order_book.asks), 0)

    def test_add_limit_order_price_time_priority(self):
        # Add multiple bids at different prices
        self.order_book.add_limit_order(Order(1, 101, Side.BID, 95, 10, 1000))
        self.order_book.add_limit_order(Order(2, 102, Side.BID, 97, 10, 1001))
        self.order_book.add_limit_order(Order(3, 103, Side.BID, 96, 10, 1002))
        
        # Bids should be sorted by price (highest first)
        self.assertEqual(self.order_book.bids[0].order_id, 2)
        self.assertEqual(self.order_book.bids[1].order_id, 3)
        self.assertEqual(self.order_book.bids[2].order_id, 1)
        
        # Add multiple asks at different prices
        self.order_book.add_limit_order(Order(4, 104, Side.ASK, 105, 10, 1003))
        self.order_book.add_limit_order(Order(5, 105, Side.ASK, 103, 10, 1004))
        self.order_book.add_limit_order(Order(6, 106, Side.ASK, 104, 10, 1005))
        
        # Asks should be sorted by price (lowest first)
        self.assertEqual(self.order_book.asks[0].order_id, 5)
        self.assertEqual(self.order_book.asks[1].order_id, 6)
        self.assertEqual(self.order_book.asks[2].order_id, 4)
        
        # Add orders at same price to test time priority
        self.order_book.add_limit_order(Order(7, 107, Side.BID, 97, 5, 1006))
        self.order_book.add_limit_order(Order(8, 108, Side.ASK, 103, 5, 1007))
        
        # Check time priority for same price
        self.assertEqual(self.order_book.bids[0].order_id, 2)
        self.assertEqual(self.order_book.bids[1].order_id, 7)
        self.assertEqual(self.order_book.asks[0].order_id, 5)
        self.assertEqual(self.order_book.asks[1].order_id, 8)

    def test_market_order_partial_fill(self):
        # Setup order book
        self.order_book.add_limit_order(Order(1, 101, Side.ASK, 100, 5, 1000))
        self.order_book.add_limit_order(Order(2, 102, Side.ASK, 101, 10, 1001))
        self.order_book.add_limit_order(Order(3, 103, Side.ASK, 102, 15, 1002))
        
        # Execute market buy order for more than available at best price
        remaining = self.order_book.execute_market_order(Side.BID, 8)
        
        # Should fill the best price completely and part of the next price level
        self.assertEqual(remaining, 0)
        self.assertEqual(len(self.order_book.asks), 2)
        self.assertEqual(self.order_book.asks[0].order_id, 2)
        self.assertEqual(self.order_book.asks[0].quantity, 7)

    def test_market_order_full_fill(self):
        # Setup order book
        self.order_book.add_limit_order(Order(1, 101, Side.BID, 100, 5, 1000))
        self.order_book.add_limit_order(Order(2, 102, Side.BID, 99, 10, 1001))
        self.order_book.add_limit_order(Order(3, 103, Side.BID, 98, 15, 1002))
        
        # Execute market sell order for exactly the top level
        remaining = self.order_book.execute_market_order(Side.ASK, 5)
        
        # Should fill the best price completely
        self.assertEqual(remaining, 0)
        self.assertEqual(len(self.order_book.bids), 2)
        self.assertEqual(self.order_book.bids[0].order_id, 2)

    def test_market_order_insufficient_liquidity(self):
        # Setup order book with limited liquidity
        self.order_book.add_limit_order(Order(1, 101, Side.BID, 100, 5, 1000))
        self.order_book.add_limit_order(Order(2, 102, Side.BID, 99, 10, 1001))
        
        # Execute market sell order for more than available
        remaining = self.order_book.execute_market_order(Side.ASK, 20)
        
        # Should fill all available orders and return remaining quantity
        self.assertEqual(remaining, 5)
        self.assertEqual(len(self.order_book.bids), 0)

    def test_cancel_order(self):
        # Add orders
        self.order_book.add_limit_order(Order(1, 101, Side.BID, 100, 10, 1000))
        self.order_book.add_limit_order(Order(2, 102, Side.ASK, 110, 10, 1001))
        
        # Cancel bid order
        self.order_book.cancel_order(1)
        
        # Check if the order is canceled
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(len(self.order_book.asks), 1)
        
        # Try to cancel again
        with self.assertRaises(Exception):
            self.order_book.cancel_order(1)
        
        # Cancel ask order
        self.order_book.cancel_order(2)
        
        # Check if the order is canceled
        self.assertEqual(len(self.order_book.asks), 0)

    def test_orderbook_size_limit(self):
        # Add max number of orders (1000) to the bid side
        for i in range(1, 1001):
            self.order_book.add_limit_order(Order(i, 100+i, Side.BID, 90, 1, 1000+i))
        
        # Adding one more should raise an exception
        with self.assertRaises(Exception):
            self.order_book.add_limit_order(Order(1001, 2001, Side.BID, 90, 1, 2001))
            
        # Test the same for ask side
        self.order_book = OrderBook()  # Reset order book
        for i in range(1, 1001):
            self.order_book.add_limit_order(Order(i, 100+i, Side.ASK, 110, 1, 1000+i))
            
        # Adding one more should raise an exception
        with self.assertRaises(Exception):
            self.order_book.add_limit_order(Order(1001, 2001, Side.ASK, 110, 1, 2001))

    def test_zero_quantity_orders(self):
        # Try to add an order with zero quantity
        with self.assertRaises(Exception):
            self.order_book.add_limit_order(Order(1, 101, Side.BID, 100, 0, 1000))
            
    def test_extreme_price_orders(self):
        # Very high buy price
        self.order_book.add_limit_order(Order(1, 101, Side.BID, 1000000, 10, 1000))
        self.assertEqual(len(self.order_book.bids), 1)
        
        # Very low sell price
        self.order_book.add_limit_order(Order(2, 102, Side.ASK, 1, 10, 1001))
        
        # These should match
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(len(self.order_book.asks), 0)
        
    def test_large_quantity_market_order(self):
        # Add some liquidity
        self.order_book.add_limit_order(Order(1, 101, Side.ASK, 100, 10, 1000))
        self.order_book.add_limit_order(Order(2, 102, Side.ASK, 101, 10, 1001))
        
        # Execute a very large market order
        remaining = self.order_book.execute_market_order(Side.BID, 1000000)
        
        # Should consume all liquidity and return remaining
        self.assertEqual(remaining, 1000000 - 20)
        self.assertEqual(len(self.order_book.asks), 0)

if __name__ == '__main__':
    unittest.main()