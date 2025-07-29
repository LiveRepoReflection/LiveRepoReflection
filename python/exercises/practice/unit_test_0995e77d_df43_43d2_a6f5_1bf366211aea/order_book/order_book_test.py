import unittest
import threading
import random
from time import sleep
from order_book import OrderBook

class TestOrderBook(unittest.TestCase):
    def setUp(self):
        # Use depth 5 for testing
        self.depth = 5
        self.ob = OrderBook(depth=self.depth)

    def test_single_bid_update(self):
        # Ingest a single bid update and check aggregated state.
        update = {
            "timestamp": 1,
            "market_maker": "MM1",
            "side": "bid",
            "price": 100.0,
            "size": 10.0
        }
        self.ob.ingest_update(update)
        top_bids = self.ob.get_top_levels("bid", self.depth)
        self.assertEqual(len(top_bids), 1)
        # For bids, highest price comes first.
        self.assertEqual(top_bids[0], (100.0, 10.0))
    
    def test_multiple_updates_same_price(self):
        # Ingest multiple updates for same price from different market makers.
        updates = [
            {"timestamp": 1, "market_maker": "MM1", "side": "bid", "price": 99.5, "size": 5.0},
            {"timestamp": 2, "market_maker": "MM2", "side": "bid", "price": 99.5, "size": 7.0},
            {"timestamp": 3, "market_maker": "MM1", "side": "bid", "price": 99.5, "size": -2.0},
        ]
        for upd in updates:
            self.ob.ingest_update(upd)
        top_bids = self.ob.get_top_levels("bid", self.depth)
        # Aggregated size should be 5.0 + 7.0 - 2.0 = 10.0 at price 99.5
        self.assertEqual(len(top_bids), 1)
        self.assertEqual(top_bids[0], (99.5, 10.0))
    
    def test_update_removal_on_zero_size(self):
        # Test that a price level is removed when aggregated size becomes zero or negative.
        updates = [
            {"timestamp": 1, "market_maker": "MM1", "side": "ask", "price": 101.0, "size": 8.0},
            {"timestamp": 2, "market_maker": "MM2", "side": "ask", "price": 101.0, "size": -8.0},
        ]
        for upd in updates:
            self.ob.ingest_update(upd)
        top_asks = self.ob.get_top_levels("ask", self.depth)
        # The level should have been removed.
        self.assertEqual(len(top_asks), 0)
    
    def test_top_n_levels_limit_bid(self):
        # Insert more than depth levels for bid side. Only the top 'depth' best prices (highest prices) must be present.
        prices = [100.0 - i for i in range(10)]  # Prices 100.0, 99.0, ... 91.0
        for i, price in enumerate(prices):
            update = {
                "timestamp": i+1,
                "market_maker": f"MM{i % 3}",
                "side": "bid",
                "price": price,
                "size": 10.0
            }
            self.ob.ingest_update(update)
        top_bids = self.ob.get_top_levels("bid", self.depth)
        # Expect top 5 highest bid levels i.e. 100.0 down to 96.0
        expected = [(price, 10.0) for price in sorted(prices, reverse=True)[:self.depth]]
        self.assertEqual(top_bids, expected)
    
    def test_top_n_levels_limit_ask(self):
        # Insert more than depth levels for ask side. Only the top 'depth' best prices (lowest prices) must be present.
        prices = [100.0 + i for i in range(10)]  # Prices 100.0, 101.0, ... 109.0
        for i, price in enumerate(prices):
            update = {
                "timestamp": i+1,
                "market_maker": f"MM{i % 2}",
                "side": "ask",
                "price": price,
                "size": 5.0
            }
            self.ob.ingest_update(update)
        top_asks = self.ob.get_top_levels("ask", self.depth)
        # Expect top 5 lowest ask levels: 100.0 to 104.0
        expected = [(price, 5.0) for price in sorted(prices)[:self.depth]]
        self.assertEqual(top_asks, expected)
    
    def test_weighted_average_price_bid(self):
        # Create multiple bid levels and calculate weighted average price.
        updates = [
            {"timestamp": 1, "market_maker": "MM1", "side": "bid", "price": 100.0, "size": 10.0},
            {"timestamp": 2, "market_maker": "MM2", "side": "bid", "price": 99.0, "size": 20.0},
            {"timestamp": 3, "market_maker": "MM3", "side": "bid", "price": 98.0, "size": 30.0},
        ]
        for upd in updates:
            self.ob.ingest_update(upd)
        wap = self.ob.get_weighted_average_price("bid")
        total_size = 10.0 + 20.0 + 30.0
        expected_wap = (100.0*10.0 + 99.0*20.0 + 98.0*30.0) / total_size
        self.assertAlmostEqual(wap, expected_wap, places=6)

    def test_weighted_average_price_ask(self):
        # Create multiple ask levels and calculate weighted average price.
        updates = [
            {"timestamp": 1, "market_maker": "MM1", "side": "ask", "price": 101.0, "size": 15.0},
            {"timestamp": 2, "market_maker": "MM2", "side": "ask", "price": 102.0, "size": 25.0},
        ]
        for upd in updates:
            self.ob.ingest_update(upd)
        wap = self.ob.get_weighted_average_price("ask")
        total_size = 15.0 + 25.0
        expected_wap = (101.0*15.0 + 102.0*25.0) / total_size
        self.assertAlmostEqual(wap, expected_wap, places=6)
    
    def test_concurrent_updates(self):
        # Test thread safety by concurrently running updates.
        def worker(updates):
            for upd in updates:
                self.ob.ingest_update(upd)
                # simulate processing time
                sleep(0.001)
        
        # Generate a list of updates for threads. We'll use random data.
        updates_thread1 = [{
            "timestamp": i,
            "market_maker": "MM1",
            "side": "bid",
            "price": 100.0 - (i % 10),
            "size": random.uniform(1.0, 5.0)
        } for i in range(1, 51)]
        
        updates_thread2 = [{
            "timestamp": i+100,
            "market_maker": "MM2",
            "side": "ask",
            "price": 101.0 + (i % 10),
            "size": random.uniform(1.0, 5.0)
        } for i in range(1, 51)]
        
        thread1 = threading.Thread(target=worker, args=(updates_thread1,))
        thread2 = threading.Thread(target=worker, args=(updates_thread2,))
        
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        # After all updates, simply check that order book does not exceed configured depth.
        top_bids = self.ob.get_top_levels("bid", self.depth)
        top_asks = self.ob.get_top_levels("ask", self.depth)
        self.assertLessEqual(len(top_bids), self.depth)
        self.assertLessEqual(len(top_asks), self.depth)
    
    def test_edge_case_negative_size(self):
        # Test scenario where an update may reduce size below zero, ensuring removal.
        updates = [
            {"timestamp": 1, "market_maker": "MM1", "side": "bid", "price": 100.0, "size": 10.0},
            {"timestamp": 2, "market_maker": "MM2", "side": "bid", "price": 100.0, "size": -15.0}
        ]
        for upd in updates:
            self.ob.ingest_update(upd)
        top_bids = self.ob.get_top_levels("bid", self.depth)
        # The level should be removed because aggregated size is negative.
        self.assertEqual(len(top_bids), 0)

if __name__ == '__main__':
    unittest.main()