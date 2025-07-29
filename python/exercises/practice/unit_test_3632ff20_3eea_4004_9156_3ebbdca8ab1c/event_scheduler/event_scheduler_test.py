import unittest
import threading
import time
from event_scheduler import schedule_event, cancel_event, get_next_events

class TestEventScheduler(unittest.TestCase):
    def setUp(self):
        # Since the scheduler is assumed to have global state, we cancel any pre-scheduled events.
        # We'll attempt to cancel events with known test prefixes.
        for i in range(1000):
            cancel_event(f"test_event_{i}")

    def test_schedule_event_success(self):
        event_id = "test_event_1"
        exec_time = int(time.time()) + 10
        payload = "payload1"
        priority = 5
        result = schedule_event(event_id, exec_time, payload, priority)
        self.assertTrue(result, "Scheduling a new event should return True")

    def test_schedule_duplicate_event(self):
        event_id = "test_event_2"
        exec_time = int(time.time()) + 20
        payload = "payload2"
        priority = 3
        result1 = schedule_event(event_id, exec_time, payload, priority)
        result2 = schedule_event(event_id, exec_time, payload, priority)
        self.assertTrue(result1, "First scheduling should succeed")
        self.assertFalse(result2, "Scheduling a duplicate event should return False")

    def test_cancel_event_success(self):
        event_id = "test_event_3"
        exec_time = int(time.time()) + 30
        payload = "payload3"
        priority = 4
        schedule_event(event_id, exec_time, payload, priority)
        result = cancel_event(event_id)
        self.assertTrue(result, "Cancelling an existing event should return True")

    def test_cancel_event_nonexistent(self):
        result = cancel_event("nonexistent_event")
        self.assertFalse(result, "Cancelling a nonexistent event should return False")

    def test_get_next_events_ordering(self):
        # Setup events with varying priorities and times
        now = int(time.time())
        events = [
            ("test_event_10", now - 1, "payload10", 5),
            ("test_event_11", now - 2, "payload11", 10),
            ("test_event_12", now - 3, "payload12", 7),
            ("test_event_13", now - 1, "payload13", 10),
            ("test_event_14", now - 4, "payload14", 5)
        ]
        # Clear any possible pre-existing events
        for e in events:
            cancel_event(e[0])
        # Schedule events
        for event_id, exec_time, payload, priority in events:
            schedule_event(event_id, exec_time, payload, priority)
        
        # Retrieve events scheduled until now (all events scheduled before current time)
        result = get_next_events(now, 10)
        
        # Expected order:
        # Among events available, highest priority first; for equal priority, sort by execution time ascending.
        # The events with priority 10: test_event_11 (exec_time = now -2) and test_event_13 (exec_time = now -1) -> order: test_event_11, test_event_13
        # Then event with priority 7: test_event_12
        # Then events with priority 5: test_event_14 (now -4), test_event_10 (now -1) -> order: test_event_14, test_event_10
        expected_order = [
            ("test_event_11", "payload11"),
            ("test_event_13", "payload13"),
            ("test_event_12", "payload12"),
            ("test_event_14", "payload14"),
            ("test_event_10", "payload10")
        ]
        self.assertEqual(result, expected_order, "Events should be retrieved in the correct priority and execution time order")
        
        # Ensure that the events are removed after retrieval
        result_after = get_next_events(now, 10)
        self.assertEqual(result_after, [], "Events should be removed from scheduler after retrieval")

    def test_get_next_events_limit(self):
        now = int(time.time())
        # Schedule multiple events
        for i in range(5):
            event_id = f"test_event_limit_{i}"
            # All events scheduled before current time
            schedule_event(event_id, now - 1, f"payload_{i}", i)
        # Request only 3 events
        result = get_next_events(now, 3)
        self.assertEqual(len(result), 3, "Should retrieve only the number of events requested by max_events limit")
        # Clean up the remaining events
        for i in range(5):
            cancel_event(f"test_event_limit_{i}")

    def test_thread_safety(self):
        now = int(time.time())
        num_threads = 10
        events_per_thread = 50
        all_event_ids = []

        def schedule_events(thread_id):
            for i in range(events_per_thread):
                event_id = f"thread_event_{thread_id}_{i}"
                # Stagger execution times slightly
                exec_time = now - (i % 5)
                payload = f"payload_{thread_id}_{i}"
                priority = (i % 10)
                success = schedule_event(event_id, exec_time, payload, priority)
                self.assertTrue(success, f"Thread {thread_id} failed to schedule event {event_id}")
                all_event_ids.append(event_id)

        threads = []
        for t in range(num_threads):
            thread = threading.Thread(target=schedule_events, args=(t,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Retrieve all events scheduled until now.
        result = get_next_events(now, num_threads * events_per_thread)
        # Check that the number of events retrieved matches what was scheduled.
        self.assertEqual(len(result), num_threads * events_per_thread, "All scheduled events should be retrieved in a thread-safe manner")

    def test_retrieval_removes_events(self):
        now = int(time.time())
        event_id = "test_event_remove"
        schedule_event(event_id, now - 1, "payload_remove", 5)
        result1 = get_next_events(now, 1)
        self.assertIn((event_id, "payload_remove"), result1, "Scheduled event should be retrieved")
        # Second retrieval should not include the same event
        result2 = get_next_events(now, 1)
        self.assertNotIn((event_id, "payload_remove"), result2, "Event should be removed after being retrieved")

if __name__ == "__main__":
    unittest.main()