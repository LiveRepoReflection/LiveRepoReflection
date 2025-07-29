import unittest
from event_aggregator import EventAggregator

class EventAggregatorTest(unittest.TestCase):
    def setUp(self):
        # Instantiate the aggregator before each test.
        self.aggregator = EventAggregator()

    def test_empty_query(self):
        # When no events have been ingested, querying should return default values.
        result = self.aggregator.query("temperature", 1678886400, 1678886460)
        expected = {
            "metric_name": "temperature",
            "time_window_start": 1678886400,
            "time_window_end": 1678886460,
            "count": 0,
            "sum": 0.0,
            "avg": None,
            "min": None,
            "max": None
        }
        self.assertEqual(result, expected)

    def test_single_event(self):
        # Ingest a single event and verify the aggregates.
        event = {
            "device_id": "dev1",
            "timestamp": 1678886410,
            "metric_name": "temperature",
            "metric_value": 25.0
        }
        self.aggregator.ingest_event(event)
        result = self.aggregator.query("temperature", 1678886400, 1678886460)
        expected = {
            "metric_name": "temperature",
            "time_window_start": 1678886400,
            "time_window_end": 1678886460,
            "count": 1,
            "sum": 25.0,
            "avg": 25.0,
            "min": 25.0,
            "max": 25.0
        }
        self.assertEqual(result, expected)

    def test_multiple_events(self):
        # Ingest multiple events in order and verify aggregates.
        events = [
            {"device_id": "dev1", "timestamp": 1678886410, "metric_name": "temperature", "metric_value": 20.0},
            {"device_id": "dev2", "timestamp": 1678886415, "metric_name": "temperature", "metric_value": 30.0},
            {"device_id": "dev3", "timestamp": 1678886420, "metric_name": "temperature", "metric_value": 25.0},
        ]
        for event in events:
            self.aggregator.ingest_event(event)
        result = self.aggregator.query("temperature", 1678886400, 1678886460)
        expected = {
            "metric_name": "temperature",
            "time_window_start": 1678886400,
            "time_window_end": 1678886460,
            "count": 3,
            "sum": 75.0,
            "avg": 25.0,
            "min": 20.0,
            "max": 30.0
        }
        self.assertEqual(result, expected)

    def test_multiple_metrics(self):
        # Ingest events with different metric names and ensure that only relevant events are aggregated.
        events = [
            {"device_id": "dev1", "timestamp": 1678886410, "metric_name": "temperature", "metric_value": 20.0},
            {"device_id": "dev2", "timestamp": 1678886415, "metric_name": "humidity", "metric_value": 50.0},
            {"device_id": "dev3", "timestamp": 1678886420, "metric_name": "temperature", "metric_value": 30.0},
            {"device_id": "dev4", "timestamp": 1678886425, "metric_name": "humidity", "metric_value": 45.0},
        ]
        for event in events:
            self.aggregator.ingest_event(event)
        result_temp = self.aggregator.query("temperature", 1678886400, 1678886460)
        expected_temp = {
            "metric_name": "temperature",
            "time_window_start": 1678886400,
            "time_window_end": 1678886460,
            "count": 2,
            "sum": 50.0,
            "avg": 25.0,
            "min": 20.0,
            "max": 30.0
        }
        result_hum = self.aggregator.query("humidity", 1678886400, 1678886460)
        expected_hum = {
            "metric_name": "humidity",
            "time_window_start": 1678886400,
            "time_window_end": 1678886460,
            "count": 2,
            "sum": 95.0,
            "avg": 47.5,
            "min": 45.0,
            "max": 50.0
        }
        self.assertEqual(result_temp, expected_temp)
        self.assertEqual(result_hum, expected_hum)

    def test_events_outside_window(self):
        # Ingest events, some falling outside the query time window.
        event_inside = {
            "device_id": "d1",
            "timestamp": 1678886410,
            "metric_name": "temperature",
            "metric_value": 20.0
        }
        event_before = {
            "device_id": "d2",
            "timestamp": 1678886390,
            "metric_name": "temperature",
            "metric_value": 30.0
        }
        event_after = {
            "device_id": "d3",
            "timestamp": 1678886465,
            "metric_name": "temperature",
            "metric_value": 25.0
        }
        self.aggregator.ingest_event(event_inside)
        self.aggregator.ingest_event(event_before)
        self.aggregator.ingest_event(event_after)
        result = self.aggregator.query("temperature", 1678886400, 1678886460)
        expected = {
            "metric_name": "temperature",
            "time_window_start": 1678886400,
            "time_window_end": 1678886460,
            "count": 1,
            "sum": 20.0,
            "avg": 20.0,
            "min": 20.0,
            "max": 20.0
        }
        self.assertEqual(result, expected)

    def test_out_of_order_events(self):
        # Ingest events with out-of-order timestamps and verify the aggregation correctness.
        events = [
            {"device_id": "d1", "timestamp": 1678886420, "metric_name": "temperature", "metric_value": 20.0},
            {"device_id": "d2", "timestamp": 1678886410, "metric_name": "temperature", "metric_value": 30.0},
            {"device_id": "d3", "timestamp": 1678886430, "metric_name": "temperature", "metric_value": 25.0},
        ]
        for event in events:
            self.aggregator.ingest_event(event)
        result = self.aggregator.query("temperature", 1678886400, 1678886460)
        expected = {
            "metric_name": "temperature",
            "time_window_start": 1678886400,
            "time_window_end": 1678886460,
            "count": 3,
            "sum": 75.0,
            "avg": 25.0,
            "min": 20.0,
            "max": 30.0
        }
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()