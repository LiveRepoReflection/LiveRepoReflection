import unittest
from datetime import datetime, timedelta

class TestEventStreamAggregator(unittest.TestCase):
    def setUp(self):
        from event_stream_aggregate import EventStreamAggregator
        self.aggregator = EventStreamAggregator()
        
        # Base timestamp for testing
        self.base_ts = int(datetime(2023, 1, 1).timestamp() * 1000)
    
    def test_single_event_total(self):
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        result = self.aggregator.handle_query("total", self.base_ts, self.base_ts, "temperature")
        self.assertEqual(result, 25.5)

    def test_single_event_average(self):
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        result = self.aggregator.handle_query("average", self.base_ts, self.base_ts, "temperature")
        self.assertEqual(result, 25.5)

    def test_multiple_events_same_type(self):
        timestamps = [self.base_ts + i * 1000 for i in range(3)]
        values = [25.5, 26.0, 26.5]
        
        for ts, val in zip(timestamps, values):
            self.aggregator.process_event(ts, "temperature", val)
        
        total = self.aggregator.handle_query("total", self.base_ts, timestamps[-1], "temperature")
        self.assertEqual(total, sum(values))
        
        avg = self.aggregator.handle_query("average", self.base_ts, timestamps[-1], "temperature")
        self.assertEqual(avg, sum(values) / len(values))

    def test_out_of_order_events(self):
        self.aggregator.process_event(self.base_ts + 2000, "temperature", 26.5)
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        self.aggregator.process_event(self.base_ts + 1000, "temperature", 26.0)
        
        total = self.aggregator.handle_query("total", self.base_ts, self.base_ts + 2000, "temperature")
        self.assertEqual(total, 78.0)

    def test_multiple_event_types(self):
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        self.aggregator.process_event(self.base_ts + 1000, "humidity", 60.0)
        self.aggregator.process_event(self.base_ts + 2000, "pressure", 1013.25)
        
        top2 = self.aggregator.handle_query("topk", self.base_ts, self.base_ts + 2000, K=2)
        self.assertEqual(len(top2), 2)
        self.assertEqual(top2[0][0], "pressure")
        self.assertEqual(top2[0][1], 1013.25)

    def test_empty_time_window(self):
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        result = self.aggregator.handle_query("total", self.base_ts + 1000, self.base_ts + 2000, "temperature")
        self.assertEqual(result, 0.0)

    def test_no_matching_event_type(self):
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        result = self.aggregator.handle_query("total", self.base_ts, self.base_ts, "humidity")
        self.assertEqual(result, 0.0)

    def test_large_number_of_events(self):
        # Generate 1000 events
        for i in range(1000):
            self.aggregator.process_event(
                self.base_ts + i * 100,
                "temperature",
                25.0 + (i % 10)
            )
        
        total = self.aggregator.handle_query(
            "total",
            self.base_ts,
            self.base_ts + 100000,
            "temperature"
        )
        self.assertEqual(total, 29500.0)

    def test_multiple_events_same_timestamp(self):
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        self.aggregator.process_event(self.base_ts, "temperature", 26.5)
        
        total = self.aggregator.handle_query("total", self.base_ts, self.base_ts, "temperature")
        self.assertEqual(total, 52.0)

    def test_topk_with_ties(self):
        self.aggregator.process_event(self.base_ts, "temp1", 10.0)
        self.aggregator.process_event(self.base_ts, "temp2", 10.0)
        self.aggregator.process_event(self.base_ts, "temp3", 5.0)
        
        top2 = self.aggregator.handle_query("topk", self.base_ts, self.base_ts, K=2)
        self.assertEqual(len(top2), 2)
        self.assertEqual(top2[0][1], 10.0)
        self.assertEqual(top2[1][1], 10.0)

    def test_average_with_zero_events(self):
        avg = self.aggregator.handle_query("average", self.base_ts, self.base_ts + 1000, "temperature")
        self.assertEqual(avg, 0.0)

    def test_topk_with_insufficient_types(self):
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        self.aggregator.process_event(self.base_ts, "humidity", 60.0)
        
        top5 = self.aggregator.handle_query("topk", self.base_ts, self.base_ts, K=5)
        self.assertEqual(len(top5), 2)

    def test_boundary_conditions(self):
        # Test exact boundary timestamps
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        self.aggregator.process_event(self.base_ts + 1000, "temperature", 26.5)
        
        total = self.aggregator.handle_query("total", self.base_ts, self.base_ts + 1000, "temperature")
        self.assertEqual(total, 52.0)

    def test_large_time_window(self):
        # Test with a time window of 24 hours
        day_ms = 24 * 60 * 60 * 1000
        self.aggregator.process_event(self.base_ts, "temperature", 25.5)
        self.aggregator.process_event(self.base_ts + day_ms - 1, "temperature", 26.5)
        
        total = self.aggregator.handle_query("total", self.base_ts, self.base_ts + day_ms, "temperature")
        self.assertEqual(total, 52.0)

if __name__ == '__main__':
    unittest.main()