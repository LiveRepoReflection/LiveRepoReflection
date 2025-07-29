import unittest
from event_stream import EventStreamAggregator

class TestEventStreamAggregation(unittest.TestCase):
    def setUp(self):
        self.aggregator = EventStreamAggregator()
        self.events = [
            (1678886400, "user1", "click", 1),
            (1678886401, "user2", "purchase", 100),
            (1678886402, "user1", "click", 1),
            (1678886403, "user3", "login", 1),
            (1678886404, "user2", "click", 1),
            (1678886405, "user1", "purchase", 50),
            (1678886406, "user3", "click", 2),
            (1678886407, "user2", "purchase", 75),
            (1678886408, "user1", "login", 1),
            (1678886409, "user3", "purchase", 200),
        ]
        for event in self.events:
            self.aggregator.process_event(*event)

    def test_single_entity_single_event(self):
        result = self.aggregator.query(1678886400, 1678886402, ["user1"], "click")
        self.assertEqual(result, 2)

    def test_multiple_entities_single_event(self):
        result = self.aggregator.query(1678886403, 1678886404, ["user1", "user2"], "click")
        self.assertEqual(result, 1)

    def test_full_time_range_all_entities(self):
        result = self.aggregator.query(1678886400, 1678886409, ["user1", "user2", "user3"], "purchase")
        self.assertEqual(result, 425)

    def test_non_existent_event_type(self):
        result = self.aggregator.query(1678886400, 1678886409, ["user1"], "nonexistent")
        self.assertEqual(result, 0)

    def test_non_existent_entity(self):
        result = self.aggregator.query(1678886400, 1678886409, ["user99"], "click")
        self.assertEqual(result, 0)

    def test_empty_time_range(self):
        result = self.aggregator.query(1678886410, 1678886420, ["user1"], "click")
        self.assertEqual(result, 0)

    def test_edge_case_exact_timestamp(self):
        result = self.aggregator.query(1678886405, 1678886405, ["user1"], "purchase")
        self.assertEqual(result, 50)

    def test_multiple_event_types(self):
        result1 = self.aggregator.query(1678886400, 1678886409, ["user3"], "login")
        result2 = self.aggregator.query(1678886400, 1678886409, ["user3"], "click")
        self.assertEqual(result1, 1)
        self.assertEqual(result2, 2)

    def test_out_of_order_events(self):
        # Add an event with earlier timestamp after initial setup
        self.aggregator.process_event(1678886399, "user1", "click", 1)
        result = self.aggregator.query(1678886399, 1678886400, ["user1"], "click")
        self.assertEqual(result, 2)

    def test_high_volume_throughput(self):
        # Simulate high volume by processing many events quickly
        for i in range(1000):
            self.aggregator.process_event(1678886500 + i, f"user{i%100}", "view", 1)
        result = self.aggregator.query(1678886500, 1678887500, ["user0"], "view")
        self.assertEqual(result, 10)

if __name__ == '__main__':
    unittest.main()