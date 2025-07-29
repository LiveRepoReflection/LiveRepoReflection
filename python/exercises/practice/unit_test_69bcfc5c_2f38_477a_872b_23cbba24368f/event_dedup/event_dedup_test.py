import unittest
import json
import threading
import time

from event_dedup import ingest_event, reset_store, set_dedup_window

class TestEventDedup(unittest.TestCase):
    def setUp(self):
        # Reset the deduplication store before each test.
        reset_store()
        # Set a short deduplication window for testing purposes (1 second).
        set_dedup_window(1)

    def test_unique_event_returns_true(self):
        event = json.dumps({"event_id": "unique1", "data": "payload"})
        result = ingest_event(event)
        self.assertTrue(result, "Unique event should return True when ingested first time")

    def test_duplicate_event_returns_false(self):
        event = json.dumps({"event_id": "dup_event", "data": "payload"})
        first_result = ingest_event(event)
        second_result = ingest_event(event)
        self.assertTrue(first_result, "First ingestion should return True")
        self.assertFalse(second_result, "Duplicate ingestion should return False")

    def test_event_expires_after_window(self):
        event = json.dumps({"event_id": "expiring_event", "data": "payload"})
        first_result = ingest_event(event)
        self.assertTrue(first_result, "First ingestion should return True")
        # Wait for deduplication window to expire.
        time.sleep(1.1)
        second_result = ingest_event(event)
        self.assertTrue(second_result, "Event should be processed as new after deduplication window expires")

    def test_concurrent_ingestion(self):
        event = json.dumps({"event_id": "concurrent_event", "data": "payload"})
        results = []
        def ingest():
            res = ingest_event(event)
            results.append(res)

        threads = [threading.Thread(target=ingest) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        true_count = results.count(True)
        false_count = results.count(False)
        self.assertEqual(true_count, 1, "Only one thread should see the event as unique")
        self.assertEqual(false_count, 9, "All other threads should see the event as duplicate")

    def test_out_of_order_ingestion(self):
        # Even if events arrive out-of-order within the deduplication window,
        # they should be considered duplicates based on their event_id.
        event_original = json.dumps({"event_id": "ooo_event", "data": "original"})
        event_delayed = json.dumps({"event_id": "ooo_event", "data": "delayed"})

        # Ingest the original event.
        self.assertTrue(ingest_event(event_original), "Original event should be ingested as unique")
        # Simulate a small delay.
        time.sleep(0.5)
        # Ingest the delayed event (still within dedup window).
        self.assertFalse(ingest_event(event_delayed), "Delayed duplicate event should return False")
        # Wait until the window expires.
        time.sleep(0.6)
        # Ingest the event again after expiration.
        self.assertTrue(ingest_event(event_delayed), "Event should be considered unique after deduplication window expires")

if __name__ == "__main__":
    unittest.main()