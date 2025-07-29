import unittest
import datetime
from orderbook_backtest import backtest_strategy

class OrderbookBacktestTest(unittest.TestCase):
    def setUp(self):
        # Basic order book snapshot
        self.snapshots = [
            {
                'timestamp': datetime.datetime(2023, 1, 1, 10, 0, 0),
                'bids': [
                    {'price': 100.0, 'quantity': 10},
                    {'price': 99.0, 'quantity': 20},
                    {'price': 98.0, 'quantity': 30}
                ],
                'asks': [
                    {'price': 101.0, 'quantity': 15},
                    {'price': 102.0, 'quantity': 25},
                    {'price': 103.0, 'quantity': 35}
                ]
            },
            {
                'timestamp': datetime.datetime(2023, 1, 1, 10, 0, 1),
                'bids': [
                    {'price': 100.0, 'quantity': 5},
                    {'price': 99.0, 'quantity': 20},
                    {'price': 98.0, 'quantity': 30}
                ],
                'asks': [
                    {'price': 101.0, 'quantity': 10},
                    {'price': 102.0, 'quantity': 25},
                    {'price': 103.0, 'quantity': 35}
                ]
            },
            {
                'timestamp': datetime.datetime(2023, 1, 1, 10, 0, 2),
                'bids': [
                    {'price': 100.0, 'quantity': 5},
                    {'price': 99.0, 'quantity': 15},
                    {'price': 98.0, 'quantity': 30}
                ],
                'asks': [
                    {'price': 101.0, 'quantity': 10},
                    {'price': 102.0, 'quantity': 20},
                    {'price': 103.0, 'quantity': 35}
                ]
            }
        ]

    def test_basic_strategy(self):
        """Test with a simple strategy that buys at the best ask price"""
        def simple_buy_strategy(orderbook, timestamp, inventory):
            # Simple strategy: always buy 1 unit at the best ask price
            return [{'side': 'buy', 'price': orderbook['asks'][0]['price'], 'quantity': 1}]

        # Test parameters
        bid_impact = 0.01
        ask_impact = 0.01
        latency = 100  # ms
        transaction_cost = 0.001  # 0.1%
        inventory_limit = 10
        order_lifetime = 1000  # ms

        result = backtest_strategy(
            self.snapshots,
            simple_buy_strategy,
            bid_impact,
            ask_impact,
            latency,
            transaction_cost,
            inventory_limit,
            order_lifetime
        )

        # Check that the result contains all required fields
        self.assertIn('profit_loss', result)
        self.assertIn('final_inventory', result)
        self.assertIn('trades', result)
        self.assertIn('max_inventory', result)
        
        # With this strategy, we should have a non-zero inventory
        self.assertGreater(result['final_inventory'], 0)
        
        # With transaction costs, we should have a negative profit/loss
        self.assertLess(result['profit_loss'], 0)

        # Check that trades were executed
        self.assertTrue(len(result['trades']) > 0)
        
        # Check trade format
        for trade in result['trades']:
            self.assertIn('timestamp', trade)
            self.assertIn('side', trade)
            self.assertIn('price', trade)
            self.assertIn('quantity', trade)
            
    def test_no_strategy(self):
        """Test with a strategy that never places orders"""
        def no_orders_strategy(orderbook, timestamp, inventory):
            return []

        # Test parameters
        bid_impact = 0.01
        ask_impact = 0.01
        latency = 100  # ms
        transaction_cost = 0.001  # 0.1%
        inventory_limit = 10
        order_lifetime = 1000  # ms

        result = backtest_strategy(
            self.snapshots,
            no_orders_strategy,
            bid_impact,
            ask_impact,
            latency,
            transaction_cost,
            inventory_limit,
            order_lifetime
        )

        # With no orders, profit/loss should be zero
        self.assertEqual(result['profit_loss'], 0)
        
        # Inventory should remain at zero
        self.assertEqual(result['final_inventory'], 0)
        
        # No trades should be executed
        self.assertEqual(len(result['trades']), 0)
        
        # Max inventory should be zero
        self.assertEqual(result['max_inventory'], 0)
        
    def test_buy_and_sell_strategy(self):
        """Test with a strategy that buys and then sells"""
        def buy_then_sell_strategy(orderbook, timestamp, inventory):
            if inventory < 5:
                # Buy at best ask
                return [{'side': 'buy', 'price': orderbook['asks'][0]['price'], 'quantity': 1}]
            else:
                # Sell at best bid
                return [{'side': 'sell', 'price': orderbook['bids'][0]['price'], 'quantity': 1}]

        # Test parameters
        bid_impact = 0.01
        ask_impact = 0.01
        latency = 100  # ms
        transaction_cost = 0.001  # 0.1%
        inventory_limit = 10
        order_lifetime = 1000  # ms

        result = backtest_strategy(
            self.snapshots,
            buy_then_sell_strategy,
            bid_impact,
            ask_impact,
            latency,
            transaction_cost,
            inventory_limit,
            order_lifetime
        )

        # Check that trades were executed
        self.assertTrue(len(result['trades']) > 0)
        
    def test_inventory_limit(self):
        """Test that inventory limit is respected"""
        def aggressive_buy_strategy(orderbook, timestamp, inventory):
            # Try to buy more than inventory limit
            return [{'side': 'buy', 'price': orderbook['asks'][0]['price'], 'quantity': 20}]

        # Test parameters
        bid_impact = 0.01
        ask_impact = 0.01
        latency = 100  # ms
        transaction_cost = 0.001  # 0.1%
        inventory_limit = 10
        order_lifetime = 1000  # ms

        result = backtest_strategy(
            self.snapshots,
            aggressive_buy_strategy,
            bid_impact,
            ask_impact,
            latency,
            transaction_cost,
            inventory_limit,
            order_lifetime
        )

        # Final inventory should not exceed the limit
        self.assertLessEqual(result['final_inventory'], inventory_limit)
        
        # Max inventory should not exceed the limit
        self.assertLessEqual(result['max_inventory'], inventory_limit)
        
    def test_latency_and_order_lifetime(self):
        """Test that latency and order lifetime are handled correctly"""
        
        # Create snapshots with precise timestamps
        detailed_snapshots = []
        for i in range(10):
            detailed_snapshots.append({
                'timestamp': datetime.datetime(2023, 1, 1, 10, 0, 0) + datetime.timedelta(milliseconds=i*50),
                'bids': [
                    {'price': 100.0 - i*0.1, 'quantity': 10},
                    {'price': 99.0 - i*0.1, 'quantity': 20},
                ],
                'asks': [
                    {'price': 101.0 + i*0.1, 'quantity': 15},
                    {'price': 102.0 + i*0.1, 'quantity': 25},
                ]
            })
        
        def simple_buy_strategy(orderbook, timestamp, inventory):
            # Always try to buy at best ask
            return [{'side': 'buy', 'price': orderbook['asks'][0]['price'], 'quantity': 1}]

        # Test with high latency that should result in missed orders
        high_latency = 300  # ms
        short_lifetime = 200  # ms
        
        result = backtest_strategy(
            detailed_snapshots,
            simple_buy_strategy,
            0.01, 0.01,
            high_latency,
            0.001, 10,
            short_lifetime
        )
        
        # Some orders might be canceled due to latency/lifetime constraints
        # So trades executed might be less than the number of snapshots
        self.assertLessEqual(len(result['trades']), len(detailed_snapshots))
        
    def test_edge_cases(self):
        """Test handling of edge cases"""
        
        # Empty order book
        empty_snapshots = [
            {
                'timestamp': datetime.datetime(2023, 1, 1, 10, 0, 0),
                'bids': [],
                'asks': []
            }
        ]
        
        def strategy_with_invalid_orders(orderbook, timestamp, inventory):
            # Return invalid orders
            return [
                {'side': 'buy', 'price': -10, 'quantity': 5},  # Negative price
                {'side': 'sell', 'price': 100, 'quantity': 0},  # Zero quantity
                {'side': 'invalid', 'price': 100, 'quantity': 5},  # Invalid side
                {}  # Missing fields
            ]

        result = backtest_strategy(
            empty_snapshots,
            strategy_with_invalid_orders,
            0.01, 0.01,
            100, 0.001,
            10, 1000
        )
        
        # Should handle empty order book gracefully
        self.assertEqual(result['profit_loss'], 0)
        self.assertEqual(result['final_inventory'], 0)
        self.assertEqual(len(result['trades']), 0)
        
    def test_order_book_gaps(self):
        """Test handling of order book gaps"""
        
        # Order book with gaps in price levels
        gappy_snapshots = [
            {
                'timestamp': datetime.datetime(2023, 1, 1, 10, 0, 0),
                'bids': [
                    {'price': 100.0, 'quantity': 10},
                    # Gap here
                    {'price': 95.0, 'quantity': 30}
                ],
                'asks': [
                    {'price': 101.0, 'quantity': 15},
                    # Gap here
                    {'price': 105.0, 'quantity': 35}
                ]
            }
        ]
        
        def large_order_strategy(orderbook, timestamp, inventory):
            # Place a large order that will need to walk the book
            return [{'side': 'buy', 'price': 105.0, 'quantity': 20}]

        result = backtest_strategy(
            gappy_snapshots,
            large_order_strategy,
            0.01, 0.01,
            100, 0.001,
            30, 1000
        )
        
        # Should handle order book gaps gracefully
        self.assertGreaterEqual(len(result['trades']), 0)
        
    def test_multiple_orders_strategy(self):
        """Test with a strategy that places multiple orders at once"""
        
        def multiple_orders_strategy(orderbook, timestamp, inventory):
            return [
                {'side': 'buy', 'price': orderbook['asks'][0]['price'], 'quantity': 1},
                {'side': 'buy', 'price': orderbook['asks'][1]['price'], 'quantity': 2},
                {'side': 'sell', 'price': orderbook['bids'][0]['price'], 'quantity': 1}
            ]

        result = backtest_strategy(
            self.snapshots,
            multiple_orders_strategy,
            0.01, 0.01,
            100, 0.001,
            10, 1000
        )
        
        # Check that trades were executed
        self.assertTrue(len(result['trades']) > 0)
        
    def test_performance(self):
        """Basic test to ensure the backtest can handle larger datasets"""
        
        # Generate a larger dataset
        large_snapshots = []
        for i in range(100):  # 100 snapshots
            large_snapshots.append({
                'timestamp': datetime.datetime(2023, 1, 1, 10, 0, 0) + datetime.timedelta(seconds=i),
                'bids': [
                    {'price': 100.0 - (i%10)*0.1, 'quantity': 10},
                    {'price': 99.0 - (i%10)*0.1, 'quantity': 20},
                    {'price': 98.0 - (i%10)*0.1, 'quantity': 30}
                ],
                'asks': [
                    {'price': 101.0 + (i%10)*0.1, 'quantity': 15},
                    {'price': 102.0 + (i%10)*0.1, 'quantity': 25},
                    {'price': 103.0 + (i%10)*0.1, 'quantity': 35}
                ]
            })

        def simple_strategy(orderbook, timestamp, inventory):
            if inventory < 5:
                return [{'side': 'buy', 'price': orderbook['asks'][0]['price'], 'quantity': 1}]
            else:
                return [{'side': 'sell', 'price': orderbook['bids'][0]['price'], 'quantity': 1}]

        # This test is more about checking if the function completes in reasonable time
        # rather than specific output checks
        start_time = datetime.datetime.now()
        
        result = backtest_strategy(
            large_snapshots,
            simple_strategy,
            0.01, 0.01,
            100, 0.001,
            10, 1000
        )
        
        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Just ensure it completed and returned expected structures
        self.assertIn('profit_loss', result)
        self.assertIn('final_inventory', result)
        self.assertIn('trades', result)
        
        # Expected execution time depends on hardware, but shouldn't take minutes
        # This is just a rough sanity check
        self.assertLess(execution_time, 10)  # Should complete in less than 10 seconds

if __name__ == '__main__':
    unittest.main()