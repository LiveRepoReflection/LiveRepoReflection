import unittest
import time

# Import the functions from the realtime_analytics module.
# It is assumed that the realtime_analytics module provides the following functions:
#   - ingest_event(event: dict) -> None
#   - get_current_metrics(category_id: str) -> dict {"clicks": int, "views": int, "purchases": int}
#   - get_historical_metrics(category_id: str, start_timestamp: int, end_timestamp: int) -> dict {"clicks": int, "views": int, "purchases": int}
#   - get_top_k_categories(k: int) -> list of tuples [(category_id, purchase_count), ...]
#   - reset() -> None  (Resets the internal state for testing purposes)
from realtime_analytics import (
    ingest_event,
    get_current_metrics,
    get_historical_metrics,
    get_top_k_categories,
    reset,
)


class RealTimeAnalyticsTest(unittest.TestCase):

    def setUp(self):
        # Reset the system state before each test.
        reset()

    def test_ingest_valid_event(self):
        # Test that a valid event is ingested and the metrics are updated accordingly.
        current_time = int(time.time() * 1000)
        event = {
            "timestamp": current_time,
            "user_id": "user_1",
            "product_id": "prod_1",
            "category_id": "cat_A",
            "event_type": "click"
        }
        ingest_event(event)
        metrics = get_current_metrics("cat_A")
        self.assertEqual(metrics.get("clicks"), 1)
        self.assertEqual(metrics.get("views"), 0)
        self.assertEqual(metrics.get("purchases"), 0)

    def test_ingest_invalid_event_missing_key(self):
        # Test that an event with a missing key is handled gracefully (ignored or counted as invalid).
        current_time = int(time.time() * 1000)
        event = {
            "timestamp": current_time,
            "user_id": "user_2",
            # "product_id" missing intentionally
            "category_id": "cat_B",
            "event_type": "view"
        }
        # Ingestion of an invalid event should not update the metrics.
        ingest_event(event)
        metrics = get_current_metrics("cat_B")
        self.assertEqual(metrics.get("clicks"), 0)
        self.assertEqual(metrics.get("views"), 0)
        self.assertEqual(metrics.get("purchases"), 0)

    def test_multiple_event_aggregation(self):
        # Test multiple events aggregation for a single category.
        base_time = int(time.time() * 1000)
        events = [
            {"timestamp": base_time - 1000, "user_id": "user_1", "product_id": "prod_1", "category_id": "cat_C", "event_type": "click"},
            {"timestamp": base_time - 500, "user_id": "user_2", "product_id": "prod_2", "category_id": "cat_C", "event_type": "view"},
            {"timestamp": base_time, "user_id": "user_3", "product_id": "prod_3", "category_id": "cat_C", "event_type": "purchase"},
            {"timestamp": base_time - 200, "user_id": "user_4", "product_id": "prod_4", "category_id": "cat_C", "event_type": "click"},
        ]
        for event in events:
            ingest_event(event)
        metrics = get_current_metrics("cat_C")
        self.assertEqual(metrics.get("clicks"), 2)
        self.assertEqual(metrics.get("views"), 1)
        self.assertEqual(metrics.get("purchases"), 1)

    def test_sliding_window_expiry(self):
        # Test that events older than the 5 minute sliding window do not affect current metrics.
        # Assume 5 minutes = 300000 ms.
        current_time = int(time.time() * 1000)
        # Event that is within the window.
        event_recent = {
            "timestamp": current_time - 1000,
            "user_id": "user_5",
            "product_id": "prod_5",
            "category_id": "cat_D",
            "event_type": "view"
        }
        # Event that is just outside the window.
        event_old = {
            "timestamp": current_time - 305000,
            "user_id": "user_6",
            "product_id": "prod_6",
            "category_id": "cat_D",
            "event_type": "purchase"
        }
        ingest_event(event_recent)
        ingest_event(event_old)
        metrics = get_current_metrics("cat_D")
        self.assertEqual(metrics.get("views"), 1)
        self.assertEqual(metrics.get("purchases"), 0)

    def test_out_of_order_events(self):
        # Test that events arriving out-of-order are correctly aggregated.
        base_time = int(time.time() * 1000)
        # Ingest a later event first.
        event_later = {
            "timestamp": base_time,
            "user_id": "user_7",
            "product_id": "prod_7",
            "category_id": "cat_E",
            "event_type": "click"
        }
        ingest_event(event_later)
        # Ingest an out-of-order event that belongs within the sliding window.
        event_earlier = {
            "timestamp": base_time - 2000,
            "user_id": "user_8",
            "product_id": "prod_8",
            "category_id": "cat_E",
            "event_type": "purchase"
        }
        ingest_event(event_earlier)
        metrics = get_current_metrics("cat_E")
        self.assertEqual(metrics.get("clicks"), 1)
        self.assertEqual(metrics.get("purchases"), 1)

    def test_historical_metrics(self):
        # Test historical metrics retrieval over a specified time range.
        base_time = int(time.time() * 1000)
        # Create events spanning a range of time.
        events = [
            {"timestamp": base_time - 600000, "user_id": "user_9", "product_id": "prod_9", "category_id": "cat_F", "event_type": "view"},
            {"timestamp": base_time - 300000, "user_id": "user_10", "product_id": "prod_10", "category_id": "cat_F", "event_type": "click"},
            {"timestamp": base_time - 100000, "user_id": "user_11", "product_id": "prod_11", "category_id": "cat_F", "event_type": "purchase"},
        ]
        for event in events:
            ingest_event(event)
        # Query historical metrics for last 400000 ms.
        start_range = base_time - 400000
        end_range = base_time
        historical = get_historical_metrics("cat_F", start_range, end_range)
        # Only event at timestamp base_time - 300000 and base_time - 100000 should be counted.
        self.assertEqual(historical.get("clicks"), 1)
        self.assertEqual(historical.get("purchases"), 1)
        self.assertEqual(historical.get("views"), 0)

    def test_top_k_categories(self):
        # Test retrieval of top K categories based on purchase counts within the current sliding window.
        current_time = int(time.time() * 1000)
        # Ingest events across multiple categories.
        events = [
            {"timestamp": current_time, "user_id": "user_12", "product_id": "prod_12", "category_id": "cat_G", "event_type": "purchase"},
            {"timestamp": current_time, "user_id": "user_13", "product_id": "prod_13", "category_id": "cat_H", "event_type": "purchase"},
            {"timestamp": current_time, "user_id": "user_14", "product_id": "prod_14", "category_id": "cat_H", "event_type": "purchase"},
            {"timestamp": current_time, "user_id": "user_15", "product_id": "prod_15", "category_id": "cat_I", "event_type": "click"},
            {"timestamp": current_time, "user_id": "user_16", "product_id": "prod_16", "category_id": "cat_J", "event_type": "purchase"},
            {"timestamp": current_time, "user_id": "user_17", "product_id": "prod_17", "category_id": "cat_J", "event_type": "purchase"},
            {"timestamp": current_time, "user_id": "user_18", "product_id": "prod_18", "category_id": "cat_J", "event_type": "purchase"},
        ]
        for event in events:
            ingest_event(event)
        # Query top 2 categories.
        top_k = get_top_k_categories(2)
        # Expected result: cat_J with 3 purchases and cat_H with 2 purchases.
        expected = [("cat_J", 3), ("cat_H", 2)]
        self.assertEqual(top_k, expected)

    def test_no_events(self):
        # Test the behavior when there are no events ingested.
        metrics = get_current_metrics("non_existent_cat")
        self.assertEqual(metrics.get("clicks"), 0)
        self.assertEqual(metrics.get("views"), 0)
        self.assertEqual(metrics.get("purchases"), 0)
        historical = get_historical_metrics("non_existent_cat", 0, int(time.time() * 1000))
        self.assertEqual(historical.get("clicks"), 0)
        self.assertEqual(historical.get("views"), 0)
        self.assertEqual(historical.get("purchases"), 0)
        top_k = get_top_k_categories(5)
        self.assertEqual(top_k, [])

if __name__ == "__main__":
    unittest.main()