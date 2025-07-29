import unittest
from threading import Thread
import time
from queue import Queue
from typing import List, Tuple
import random

class OrderBookTest(unittest.TestCase):
    def setUp(self):
        # Import here to avoid circular imports
        from decentralized_orderbook import OrderBook
        self.order_book = OrderBook()

    def test_basic_order_insertion(self):
        """Test basic order insertion functionality"""
        order = ("order1", "trader1", "buy", 100, 10)
        self.order_book.submit_order(order)
        self.assertEqual(len(self.order_book.get_buy_orders()), 1)
        self.assertEqual(len(self.order_book.get_sell_orders()), 0)

    def test_simple_match(self):
        """Test basic order matching"""
        buy_order = ("order1", "trader1", "buy", 100, 10)
        sell_order = ("order2", "trader2", "sell", 100, 10)
        
        self.order_book.submit_order(buy_order)
        trades = self.order_book.submit_order(sell_order)
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0], ("order1", "order2", 100, 10))
        self.assertEqual(len(self.order_book.get_buy_orders()), 0)
        self.assertEqual(len(self.order_book.get_sell_orders()), 0)

    def test_partial_match(self):
        """Test partial order matching"""
        buy_order = ("order1", "trader1", "buy", 100, 20)
        sell_order = ("order2", "trader2", "sell", 100, 10)
        
        self.order_book.submit_order(buy_order)
        trades = self.order_book.submit_order(sell_order)
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0], ("order1", "order2", 100, 10))
        self.assertEqual(len(self.order_book.get_buy_orders()), 1)
        self.assertEqual(self.order_book.get_buy_orders()[0][4], 10)  # Check remaining quantity

    def test_price_time_priority(self):
        """Test price-time priority matching"""
        # Submit buy orders
        self.order_book.submit_order(("order1", "trader1", "buy", 100, 10))
        self.order_book.submit_order(("order2", "trader2", "buy", 101, 10))
        
        # Submit sell order that should match with highest price buy order
        trades = self.order_book.submit_order(("order3", "trader3", "sell", 100, 10))
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0][0], "order2")  # Should match with order2 (higher price)

    def test_order_cancellation(self):
        """Test order cancellation"""
        order = ("order1", "trader1", "buy", 100, 10)
        self.order_book.submit_order(order)
        self.assertTrue(self.order_book.cancel_order("order1"))
        self.assertEqual(len(self.order_book.get_buy_orders()), 0)

    def test_concurrent_order_submission(self):
        """Test concurrent order submission"""
        def submit_orders(orders: List[Tuple], results: Queue):
            for order in orders:
                trades = self.order_book.submit_order(order)
                results.put(trades)

        # Create buy and sell orders
        buy_orders = [
            ("buy1", "trader1", "buy", 100, 10),
            ("buy2", "trader2", "buy", 101, 10),
        ]
        sell_orders = [
            ("sell1", "trader3", "sell", 100, 10),
            ("sell2", "trader4", "sell", 99, 10),
        ]

        results = Queue()
        
        # Create and start threads
        thread1 = Thread(target=submit_orders, args=(buy_orders, results))
        thread2 = Thread(target=submit_orders, args=(sell_orders, results))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()

        # Collect all trades
        all_trades = []
        while not results.empty():
            trades = results.get()
            all_trades.extend(trades)

        # Should have at least 2 trades
        self.assertGreaterEqual(len(all_trades), 2)

    def test_invalid_orders(self):
        """Test invalid order handling"""
        # Invalid price
        with self.assertRaises(ValueError):
            self.order_book.submit_order(("order1", "trader1", "buy", -100, 10))

        # Invalid quantity
        with self.assertRaises(ValueError):
            self.order_book.submit_order(("order2", "trader2", "buy", 100, 0))

        # Invalid side
        with self.assertRaises(ValueError):
            self.order_book.submit_order(("order3", "trader3", "invalid", 100, 10))

    def test_stress_test(self):
        """Stress test with many concurrent orders"""
        def generate_random_orders(n: int) -> List[Tuple]:
            orders = []
            for i in range(n):
                side = random.choice(["buy", "sell"])
                price = random.randint(90, 110)
                quantity = random.randint(1, 20)
                orders.append((f"order{i}", f"trader{i}", side, price, quantity))
            return orders

        def submit_orders(orders: List[Tuple], results: Queue):
            for order in orders:
                trades = self.order_book.submit_order(order)
                results.put(trades)
                time.sleep(0.001)  # Small delay to simulate network latency

        num_orders = 100
        num_threads = 4
        orders_per_thread = num_orders // num_threads
        
        all_orders = [generate_random_orders(orders_per_thread) for _ in range(num_threads)]
        results = Queue()
        
        threads = []
        for orders in all_orders:
            thread = Thread(target=submit_orders, args=(orders, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify the final state
        buy_orders = self.order_book.get_buy_orders()
        sell_orders = self.order_book.get_sell_orders()
        
        # Verify price ordering
        for i in range(len(buy_orders) - 1):
            self.assertGreaterEqual(buy_orders[i][3], buy_orders[i+1][3])
        
        for i in range(len(sell_orders) - 1):
            self.assertLessEqual(sell_orders[i][3], sell_orders[i+1][3])

if __name__ == '__main__':
    unittest.main()