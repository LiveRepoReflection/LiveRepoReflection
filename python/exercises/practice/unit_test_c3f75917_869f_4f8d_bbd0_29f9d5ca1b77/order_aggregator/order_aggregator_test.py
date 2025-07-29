import unittest
import time
import threading
from order_aggregator.order_aggregator import OrderBookAggregator, Order

class TestOrderAggregator(unittest.TestCase):
    def setUp(self):
        # Initialize the aggregator with a 5000ms stale threshold.
        self.aggregator = OrderBookAggregator(stale_threshold=5000)

    def test_new_order_bid(self):
        current_time = int(time.time() * 1000)
        order = Order(exchange_id="ExchangeA", order_id=1, timestamp=current_time,
                      side="BID", price=100.0, quantity=100, action="NEW")
        self.aggregator.process_order(order)
        top_bids = self.aggregator.get_top_n_levels("BID", 1)
        self.assertEqual(top_bids, [(100.0, 100)])

    def test_new_order_ask(self):
        current_time = int(time.time() * 1000)
        order = Order(exchange_id="ExchangeA", order_id=2, timestamp=current_time,
                      side="ASK", price=101.0, quantity=50, action="NEW")
        self.aggregator.process_order(order)
        top_asks = self.aggregator.get_top_n_levels("ASK", 1)
        self.assertEqual(top_asks, [(101.0, 50)])

    def test_amend_order(self):
        current_time = int(time.time() * 1000)
        # Place the initial order
        order = Order(exchange_id="ExchangeA", order_id=3, timestamp=current_time,
                      side="BID", price=100.0, quantity=100, action="NEW")
        self.aggregator.process_order(order)
        # Amend the order to update quantity to 150
        amended = Order(exchange_id="ExchangeA", order_id=3, timestamp=current_time + 10,
                        side="BID", price=100.0, quantity=150, action="AMEND")
        self.aggregator.process_order(amended)
        top_bids = self.aggregator.get_top_n_levels("BID", 1)
        self.assertEqual(top_bids, [(100.0, 150)])

    def test_cancel_order(self):
        current_time = int(time.time() * 1000)
        # Place an order and then cancel it
        order = Order(exchange_id="ExchangeB", order_id=5, timestamp=current_time,
                      side="ASK", price=101.5, quantity=200, action="NEW")
        self.aggregator.process_order(order)
        cancel = Order(exchange_id="ExchangeB", order_id=5, timestamp=current_time + 5,
                       side="ASK", price=101.5, quantity=0, action="CANCEL")
        self.aggregator.process_order(cancel)
        top_asks = self.aggregator.get_top_n_levels("ASK", 1)
        self.assertEqual(top_asks, [])

    def test_multiple_exchanges(self):
        # Orders with the same order_id from different exchanges should be handled separately.
        current_time = int(time.time() * 1000)
        order_a = Order(exchange_id="ExchangeA", order_id=10, timestamp=current_time,
                        side="BID", price=100.0, quantity=100, action="NEW")
        order_b = Order(exchange_id="ExchangeB", order_id=10, timestamp=current_time,
                        side="BID", price=100.0, quantity=50, action="NEW")
        self.aggregator.process_order(order_a)
        self.aggregator.process_order(order_b)
        top_bids = self.aggregator.get_top_n_levels("BID", 1)
        self.assertEqual(top_bids, [(100.0, 150)])

    def test_bid_order_priority(self):
        # Test that BID levels are aggregated correctly and sorted in descending order.
        current_time = int(time.time() * 1000)
        orders = [
            Order(exchange_id="ExchangeA", order_id=1, timestamp=current_time,
                  side="BID", price=99.0, quantity=100, action="NEW"),
            Order(exchange_id="ExchangeA", order_id=2, timestamp=current_time,
                  side="BID", price=100.0, quantity=200, action="NEW"),
            Order(exchange_id="ExchangeB", order_id=3, timestamp=current_time,
                  side="BID", price=98.5, quantity=50, action="NEW")
        ]
        for order in orders:
            self.aggregator.process_order(order)
        top_bids = self.aggregator.get_top_n_levels("BID", 2)
        self.assertEqual(top_bids, [(100.0, 200), (99.0, 100)])

    def test_ask_order_priority(self):
        # Test that ASK levels are aggregated correctly and sorted in ascending order.
        current_time = int(time.time() * 1000)
        orders = [
            Order(exchange_id="ExchangeA", order_id=1, timestamp=current_time,
                  side="ASK", price=101.0, quantity=100, action="NEW"),
            Order(exchange_id="ExchangeB", order_id=2, timestamp=current_time,
                  side="ASK", price=100.5, quantity=150, action="NEW"),
            Order(exchange_id="ExchangeA", order_id=3, timestamp=current_time,
                  side="ASK", price=102.0, quantity=50, action="NEW")
        ]
        for order in orders:
            self.aggregator.process_order(order)
        top_asks = self.aggregator.get_top_n_levels("ASK", 2)
        self.assertEqual(top_asks, [(100.5, 150), (101.0, 100)])

    def test_stale_order_handling(self):
        # Orders older than the stale threshold should be ignored.
        current_time = int(time.time() * 1000)
        stale_time = current_time - 6000  # 6 seconds ago, beyond 5 seconds threshold
        order = Order(exchange_id="ExchangeA", order_id=20, timestamp=stale_time,
                      side="BID", price=105.0, quantity=100, action="NEW")
        self.aggregator.process_order(order)
        top_bids = self.aggregator.get_top_n_levels("BID", 1)
        self.assertEqual(top_bids, [])

    def test_concurrent_order_processing(self):
        # Simulate concurrent processing of multiple orders.
        current_time = int(time.time() * 1000)
        orders = [
            Order(exchange_id="ExchangeA", order_id=i, timestamp=current_time,
                  side="BID", price=100.0 + i, quantity=10 * i, action="NEW")
            for i in range(1, 11)
        ]
        
        def process(order):
            self.aggregator.process_order(order)
        
        threads = [threading.Thread(target=process, args=(order,)) for order in orders]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        top_bids = self.aggregator.get_top_n_levels("BID", 5)
        expected = sorted([(order.price, order.quantity) for order in orders], key=lambda x: x[0], reverse=True)[:5]
        self.assertEqual(top_bids, expected)

if __name__ == "__main__":
    unittest.main()