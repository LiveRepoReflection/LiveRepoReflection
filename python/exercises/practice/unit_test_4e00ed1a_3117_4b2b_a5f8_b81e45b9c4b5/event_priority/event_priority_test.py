import unittest
from event_priority import EventPrioritySystem

class TestEventPrioritySystem(unittest.TestCase):
    def setUp(self):
        self.system = EventPrioritySystem()

    def test_add_and_get_event(self):
        self.system.add_event("evt1", 1000, 5.0, "login")
        result = self.system.get_top_k_events(1, 900, 1100)
        self.assertEqual(result, ["evt1"])

    def test_update_event(self):
        self.system.add_event("evt1", 1000, 5.0, "login")
        # Update existing event with new timestamp and priority
        self.system.add_event("evt1", 1050, 7.0, "login")
        result = self.system.get_top_k_events(1, 1000, 1100)
        self.assertEqual(result, ["evt1"])

    def test_remove_event(self):
        self.system.add_event("evt1", 1000, 5.0, "login")
        self.system.add_event("evt2", 1010, 7.0, "purchase")
        self.system.remove_event("evt1")
        result = self.system.get_top_k_events(2, 900, 1100)
        self.assertEqual(result, ["evt2"])

    def test_get_top_k_order_priority(self):
        # Add multiple events with varying priorities and timestamps
        self.system.add_event("evt1", 1000, 5.0, "login")
        self.system.add_event("evt2", 1010, 7.0, "login")
        self.system.add_event("evt3", 1020, 7.0, "login")  # same priority as evt2, later timestamp
        top_two = self.system.get_top_k_events(2, 900, 1100)
        # Expected order: evt2 (priority 7.0, timestamp 1010) then evt3 (priority 7.0, timestamp 1020)
        self.assertEqual(top_two, ["evt2", "evt3"])

    def test_get_top_k_with_event_types(self):
        # Add events of different types
        self.system.add_event("evt1", 1000, 5.0, "login")
        self.system.add_event("evt2", 1005, 8.0, "purchase")
        self.system.add_event("evt3", 1010, 6.0, "error")
        result = self.system.get_top_k_events(3, 900, 1100, event_types=["purchase", "error"])
        # Expected order: evt2 then evt3
        self.assertEqual(result, ["evt2", "evt3"])

    def test_get_top_k_limit(self):
        self.system.add_event("evt1", 1000, 5.0, "login")
        self.system.add_event("evt2", 1001, 7.0, "login")
        self.system.add_event("evt3", 1002, 6.0, "login")
        result = self.system.get_top_k_events(2, 900, 1100)
        # Only the two highest priority events should be returned.
        self.assertEqual(len(result), 2)
        self.assertIn("evt2", result)
        self.assertIn("evt3", result)

    def test_get_top_k_empty(self):
        result = self.system.get_top_k_events(5, 900, 1100)
        self.assertEqual(result, [])

    def test_time_window_filtering(self):
        self.system.add_event("evt1", 800, 5.0, "login")
        self.system.add_event("evt2", 900, 6.0, "login")
        self.system.add_event("evt3", 1000, 7.0, "login")
        self.system.add_event("evt4", 1100, 8.0, "login")
        # Expected to include only events within 850 to 1050: evt2 and evt3.
        result = self.system.get_top_k_events(5, 850, 1050)
        self.assertEqual(set(result), set(["evt2", "evt3"]))

    def test_tie_break_by_timestamp(self):
        # Two events with same priority, one with an earlier timestamp.
        self.system.add_event("evt1", 1000, 10.0, "login")
        self.system.add_event("evt2", 990, 10.0, "login")
        result = self.system.get_top_k_events(2, 900, 1100)
        self.assertEqual(result, ["evt2", "evt1"])

    def test_get_top_k_large_k(self):
        # When k is larger than the number of events.
        self.system.add_event("evt1", 1000, 5.0, "login")
        result = self.system.get_top_k_events(10, 900, 1100)
        self.assertEqual(result, ["evt1"])

if __name__ == "__main__":
    unittest.main()