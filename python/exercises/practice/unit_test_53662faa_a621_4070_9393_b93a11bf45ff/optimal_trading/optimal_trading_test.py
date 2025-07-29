import unittest
from optimal_trading import trading_algorithm

class MockOrderBookSnapshot:
    def __init__(self, timestamp, bids, asks, mid_price):
        self.snapshot = {
            'timestamp': timestamp,
            'bids': bids,
            'asks': asks,
            'mid_price': mid_price
        }

class OptimalTradingTest(unittest.TestCase):
    def setUp(self):
        # Define common test parameters
        self.current_inventory = 0
        self.last_trade_timestamp = 0
    
    def test_basic_functionality(self):
        # Test basic functionality with a simple snapshot
        snapshot = {
            'timestamp': 1000,
            'bids': [(99.5, 100), (99.4, 200), (99.3, 300)],
            'asks': [(100.5, 100), (100.6, 200), (100.7, 300)],
            'mid_price': 100.0
        }
        
        action, quantity = trading_algorithm(snapshot, self.current_inventory, self.last_trade_timestamp)
        # Just verifying that the function returns proper structure
        self.assertIn(action, ["BUY", "SELL", None])
        self.assertIsInstance(quantity, int)
        self.assertGreaterEqual(quantity, 0)

    def test_with_different_inventory_levels(self):
        snapshot = {
            'timestamp': 1000,
            'bids': [(99.5, 100), (99.4, 200), (99.3, 300)],
            'asks': [(100.5, 100), (100.6, 200), (100.7, 300)],
            'mid_price': 100.0
        }
        
        # Test with positive inventory
        action1, quantity1 = trading_algorithm(snapshot, 50, self.last_trade_timestamp)
        self.assertIn(action1, ["BUY", "SELL", None])
        self.assertIsInstance(quantity1, int)
        
        # Test with negative inventory
        action2, quantity2 = trading_algorithm(snapshot, -50, self.last_trade_timestamp)
        self.assertIn(action2, ["BUY", "SELL", None])
        self.assertIsInstance(quantity2, int)
        
        # Test with zero inventory
        action3, quantity3 = trading_algorithm(snapshot, 0, self.last_trade_timestamp)
        self.assertIn(action3, ["BUY", "SELL", None])
        self.assertIsInstance(quantity3, int)

    def test_with_different_mid_prices(self):
        # Test with different mid prices
        low_price_snapshot = {
            'timestamp': 1000,
            'bids': [(89.5, 100), (89.4, 200), (89.3, 300)],
            'asks': [(90.5, 100), (90.6, 200), (90.7, 300)],
            'mid_price': 90.0
        }
        
        high_price_snapshot = {
            'timestamp': 1000,
            'bids': [(109.5, 100), (109.4, 200), (109.3, 300)],
            'asks': [(110.5, 100), (110.6, 200), (110.7, 300)],
            'mid_price': 110.0
        }
        
        action_low, quantity_low = trading_algorithm(low_price_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_low, ["BUY", "SELL", None])
        self.assertIsInstance(quantity_low, int)
        
        action_high, quantity_high = trading_algorithm(high_price_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_high, ["BUY", "SELL", None])
        self.assertIsInstance(quantity_high, int)

    def test_with_different_order_book_depths(self):
        # Test with shallow order book
        shallow_snapshot = {
            'timestamp': 1000,
            'bids': [(99.5, 100)],
            'asks': [(100.5, 100)],
            'mid_price': 100.0
        }
        
        # Test with deep order book
        deep_snapshot = {
            'timestamp': 1000,
            'bids': [(99.5, 100), (99.4, 200), (99.3, 300), (99.2, 400), (99.1, 500)],
            'asks': [(100.5, 100), (100.6, 200), (100.7, 300), (100.8, 400), (100.9, 500)],
            'mid_price': 100.0
        }
        
        action_shallow, quantity_shallow = trading_algorithm(shallow_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_shallow, ["BUY", "SELL", None])
        self.assertIsInstance(quantity_shallow, int)
        
        action_deep, quantity_deep = trading_algorithm(deep_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_deep, ["BUY", "SELL", None])
        self.assertIsInstance(quantity_deep, int)

    def test_with_imbalanced_order_book(self):
        # Test with more bids than asks
        more_bids_snapshot = {
            'timestamp': 1000,
            'bids': [(99.5, 300), (99.4, 400), (99.3, 500)],
            'asks': [(100.5, 100), (100.6, 200)],
            'mid_price': 100.0
        }
        
        # Test with more asks than bids
        more_asks_snapshot = {
            'timestamp': 1000,
            'bids': [(99.5, 100), (99.4, 200)],
            'asks': [(100.5, 300), (100.6, 400), (100.7, 500)],
            'mid_price': 100.0
        }
        
        action_more_bids, quantity_more_bids = trading_algorithm(more_bids_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_more_bids, ["BUY", "SELL", None])
        self.assertIsInstance(quantity_more_bids, int)
        
        action_more_asks, quantity_more_asks = trading_algorithm(more_asks_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_more_asks, ["BUY", "SELL", None])
        self.assertIsInstance(quantity_more_asks, int)

    def test_with_different_timestamps(self):
        snapshot1 = {
            'timestamp': 1000,
            'bids': [(99.5, 100), (99.4, 200), (99.3, 300)],
            'asks': [(100.5, 100), (100.6, 200), (100.7, 300)],
            'mid_price': 100.0
        }
        
        snapshot2 = {
            'timestamp': 2000,
            'bids': [(99.5, 100), (99.4, 200), (99.3, 300)],
            'asks': [(100.5, 100), (100.6, 200), (100.7, 300)],
            'mid_price': 100.0
        }
        
        # Test with no trade yet
        action1, quantity1 = trading_algorithm(snapshot1, self.current_inventory, 0)
        self.assertIn(action1, ["BUY", "SELL", None])
        
        # Test with recent trade
        action2, quantity2 = trading_algorithm(snapshot2, self.current_inventory, 1990)
        self.assertIn(action2, ["BUY", "SELL", None])
        
        # Test with old trade
        action3, quantity3 = trading_algorithm(snapshot2, self.current_inventory, 500)
        self.assertIn(action3, ["BUY", "SELL", None])

    def test_with_price_trend(self):
        # Create a series of snapshots with increasing prices
        snapshots_increasing = [
            {
                'timestamp': 1000 + i*100,
                'bids': [(99.5 + i*0.5, 100), (99.4 + i*0.5, 200)],
                'asks': [(100.5 + i*0.5, 100), (100.6 + i*0.5, 200)],
                'mid_price': 100.0 + i*0.5
            }
            for i in range(5)
        ]
        
        # Create a series of snapshots with decreasing prices
        snapshots_decreasing = [
            {
                'timestamp': 1000 + i*100,
                'bids': [(99.5 - i*0.5, 100), (99.4 - i*0.5, 200)],
                'asks': [(100.5 - i*0.5, 100), (100.6 - i*0.5, 200)],
                'mid_price': 100.0 - i*0.5
            }
            for i in range(5)
        ]
        
        # Test with increasing prices
        last_timestamp = 0
        for snapshot in snapshots_increasing:
            action, quantity = trading_algorithm(snapshot, self.current_inventory, last_timestamp)
            self.assertIn(action, ["BUY", "SELL", None])
            last_timestamp = snapshot['timestamp']
        
        # Test with decreasing prices
        last_timestamp = 0
        for snapshot in snapshots_decreasing:
            action, quantity = trading_algorithm(snapshot, self.current_inventory, last_timestamp)
            self.assertIn(action, ["BUY", "SELL", None])
            last_timestamp = snapshot['timestamp']

    def test_with_extreme_values(self):
        # Test with extremely high prices
        high_price_snapshot = {
            'timestamp': 1000,
            'bids': [(9995.0, 100), (9994.0, 200)],
            'asks': [(10005.0, 100), (10006.0, 200)],
            'mid_price': 10000.0
        }
        
        # Test with extremely low prices
        low_price_snapshot = {
            'timestamp': 1000,
            'bids': [(0.95, 100), (0.94, 200)],
            'asks': [(1.05, 100), (1.06, 200)],
            'mid_price': 1.0
        }
        
        # Test with extremely high volume
        high_volume_snapshot = {
            'timestamp': 1000,
            'bids': [(99.5, 10000), (99.4, 20000)],
            'asks': [(100.5, 10000), (100.6, 20000)],
            'mid_price': 100.0
        }
        
        action_high_price, quantity_high_price = trading_algorithm(high_price_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_high_price, ["BUY", "SELL", None])
        
        action_low_price, quantity_low_price = trading_algorithm(low_price_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_low_price, ["BUY", "SELL", None])
        
        action_high_volume, quantity_high_volume = trading_algorithm(high_volume_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_high_volume, ["BUY", "SELL", None])

    def test_with_large_spread(self):
        # Test with large spread
        large_spread_snapshot = {
            'timestamp': 1000,
            'bids': [(95.0, 100), (94.0, 200)],
            'asks': [(105.0, 100), (106.0, 200)],
            'mid_price': 100.0
        }
        
        # Test with small spread
        small_spread_snapshot = {
            'timestamp': 1000,
            'bids': [(99.9, 100), (99.8, 200)],
            'asks': [(100.1, 100), (100.2, 200)],
            'mid_price': 100.0
        }
        
        action_large_spread, quantity_large_spread = trading_algorithm(large_spread_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_large_spread, ["BUY", "SELL", None])
        
        action_small_spread, quantity_small_spread = trading_algorithm(small_spread_snapshot, self.current_inventory, self.last_trade_timestamp)
        self.assertIn(action_small_spread, ["BUY", "SELL", None])

if __name__ == '__main__':
    unittest.main()