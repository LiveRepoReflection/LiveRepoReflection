import unittest
import random
from order_stream import OrderStream

class TestOrderStream(unittest.TestCase):

    def setUp(self):
        # Create a new instance for each test
        self.stream = OrderStream()

    def test_basic_order_processing(self):
        # Sample events as given in the example
        events = [
            (1678886400000, "order1", "buy", 100.0, 100, "new"),
            (1678886400001, "order2", "buy", 99.5, 50, "new"),
            (1678886400002, "order3", "sell", 100.5, 75, "new"),
            (1678886400003, "order1", "buy", 100.0, 50, "execute"),  # Partially execute order1, remaining order1 = 50
            (1678886400004, "order4", "sell", 101.0, 25, "new"),
            (1678886400005, "order2", "buy", 99.5, 50, "cancel")      # Cancel order2, quantity becomes 0
        ]
        for event in events:
            self.stream.process_event(event)

        # For buy side: sorted descending by price.
        # level for price 100.0 should sum active orders: order1 = 50.
        # level for price 99.5 should sum active orders: order2 canceled => 0.
        buy_book = self.stream.get_order_book("buy", 2)
        expected_buy = [(100.0, 50), (99.5, 0)]
        self.assertEqual(buy_book, expected_buy)

        # For sell side: sorted ascending by price.
        # level for price 100.5: order3 = 75.
        sell_book = self.stream.get_order_book("sell", 1)
        expected_sell = [(100.5, 75)]
        self.assertEqual(sell_book, expected_sell)

    def test_execute_order_full_and_partial(self):
        # Create a new order and then execute it partially then fully
        events = [
            (1678886400100, "orderA", "buy", 101.0, 200, "new"),
            (1678886400200, "orderA", "buy", 101.0, 50, "execute"),  # Remaining 150
            (1678886400300, "orderA", "buy", 101.0, 150, "execute")  # Remaining 0, should be removed or zeroed
        ]
        for event in events:
            self.stream.process_event(event)

        # Even if orderA reaches 0 quantity, the price level should be shown if queried.
        buy_book = self.stream.get_order_book("buy", 1)
        expected_buy = [(101.0, 0)]
        self.assertEqual(buy_book, expected_buy)

    def test_out_of_order_events(self):
        # Simulate events arriving slightly out-of-order
        events = [
            (1678886401000, "orderB", "sell", 102.0, 100, "new"),
            (1678886401005, "orderC", "sell", 102.5, 200, "new"),
            (1678886401003, "orderB", "sell", 102.0, 30, "execute"),  # Should be processed between the above events
            (1678886401010, "orderC", "sell", 102.5, 200, "cancel")
        ]
        # Shuffle events slightly to simulate out-of-order arrival
        random.shuffle(events)
        for event in events:
            self.stream.process_event(event)

        # For sell side: 
        # For price 102.0: orderB remaining: 100 - 30 = 70.
        # For price 102.5: orderC canceled -> quantity 0.
        sell_book = self.stream.get_order_book("sell", 2)
        expected_sell = [(102.0, 70), (102.5, 0)]
        self.assertEqual(sell_book, expected_sell)

    def test_duplicate_order_id(self):
        # Process duplicate new orders with same order_id; second "new" should be ignored.
        events = [
            (1678886402000, "dupOrder", "buy", 103.0, 100, "new"),
            (1678886402001, "dupOrder", "buy", 103.0, 50, "new"),  # Duplicate, should be ignored
            (1678886402002, "dupOrder", "buy", 103.0, 30, "execute")  # Execute should reduce from 100 to 70
        ]
        for event in events:
            self.stream.process_event(event)

        buy_book = self.stream.get_order_book("buy", 1)
        expected_buy = [(103.0, 70)]
        self.assertEqual(buy_book, expected_buy)

    def test_event_for_nonexistent_order(self):
        # Sending cancel and execute events for orders that were never added
        events = [
            (1678886403000, "fakeOrder1", "sell", 104.0, 50, "cancel"),
            (1678886403001, "fakeOrder2", "buy", 104.5, 50, "execute")
        ]
        for event in events:
            self.stream.process_event(event)
        # Since no valid orders, get_order_book should return empty lists.
        buy_book = self.stream.get_order_book("buy", 1)
        sell_book = self.stream.get_order_book("sell", 1)
        self.assertEqual(buy_book, [])
        self.assertEqual(sell_book, [])

    def test_invalid_execute_quantity(self):
        # Test that execute events with non-positive quantity are handled (ignored)
        events = [
            (1678886404000, "orderInvalid", "sell", 105.0, 100, "new"),
            (1678886404001, "orderInvalid", "sell", 105.0, 0, "execute"),   # Zero quantity, ignore
            (1678886404002, "orderInvalid", "sell", 105.0, -10, "execute")  # Negative quantity, ignore
        ]
        for event in events:
            self.stream.process_event(event)

        sell_book = self.stream.get_order_book("sell", 1)
        expected_sell = [(105.0, 100)]
        self.assertEqual(sell_book, expected_sell)

    def test_depth_larger_than_levels(self):
        # Test get_order_book when depth is larger than number of available price levels
        events = [
            (1678886405000, "orderD", "buy", 106.0, 150, "new"),
            (1678886405001, "orderE", "buy", 105.5, 200, "new")
        ]
        for event in events:
            self.stream.process_event(event)

        # Request depth 5, but only 2 levels available. The result should only contain 2 levels.
        buy_book = self.stream.get_order_book("buy", 5)
        expected_buy = [(106.0, 150), (105.5, 200)]
        self.assertEqual(buy_book, expected_buy)

    def test_multiple_orders_same_price(self):
        # Test aggregation of multiple orders on same price level.
        events = [
            (1678886406000, "orderF1", "sell", 107.0, 100, "new"),
            (1678886406001, "orderF2", "sell", 107.0, 150, "new"),
            (1678886406002, "orderF3", "sell", 107.0, 50, "new"),
            (1678886406003, "orderF2", "sell", 107.0, 50, "execute")  # orderF2 now becomes 100
        ]
        for event in events:
            self.stream.process_event(event)

        # Total at price 107.0: 100 + 100 (updated orderF2) + 50 = 250
        sell_book = self.stream.get_order_book("sell", 1)
        expected_sell = [(107.0, 250)]
        self.assertEqual(sell_book, expected_sell)

    def test_mixed_side_orders(self):
        # Test that orders on different sides do not interfere.
        events = [
            (1678886407000, "orderG", "buy", 108.0, 120, "new"),
            (1678886407001, "orderH", "sell", 108.5, 80, "new"),
            (1678886407002, "orderI", "buy", 107.5, 200, "new"),
            (1678886407003, "orderJ", "sell", 108.0, 60, "new")
        ]
        for event in events:
            self.stream.process_event(event)

        buy_book = self.stream.get_order_book("buy", 2)
        # Buy side sorted descending by price: 108.0 then 107.5
        expected_buy = [(108.0, 120), (107.5, 200)]
        self.assertEqual(buy_book, expected_buy)

        sell_book = self.stream.get_order_book("sell", 2)
        # Sell side sorted ascending by price: 108.0 then 108.5
        expected_sell = [(108.0, 60), (108.5, 80)]
        self.assertEqual(sell_book, expected_sell)

if __name__ == '__main__':
    unittest.main()