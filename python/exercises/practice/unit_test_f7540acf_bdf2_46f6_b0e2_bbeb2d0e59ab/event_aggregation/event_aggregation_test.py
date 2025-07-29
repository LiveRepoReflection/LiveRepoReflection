import unittest
import time

from event_aggregation.event_aggregation import EventAggregator

class TestEventAggregator(unittest.TestCase):
    def setUp(self):
        # Use a sliding window of 5000 milliseconds and an error bound of 5%
        # The implementation of EventAggregator is assumed to support these parameters.
        self.window = 5000
        self.error_bound = 0.05
        self.aggregator = EventAggregator(window=self.window, error_bound=self.error_bound)

    def get_current_time(self):
        # For testing purposes, we use a fixed current time
        return 1000000

    def test_empty_category(self):
        # For a category with no events, expect get_median to return None.
        current_time = self.get_current_time()
        median = self.aggregator.get_median("nonexistent", current_time)
        self.assertIsNone(median, "Median for a category with no events should be None")

    def test_single_event(self):
        current_time = self.get_current_time()
        event = (current_time - 1000, "A", 42, 1)
        self.aggregator.add_event(event)
        median = self.aggregator.get_median("A", current_time)
        self.assertEqual(median, 42, "Median of a single event should be equal to its value")

    def test_multiple_events_exact_median(self):
        # Add an odd number of events so the true median is the middle element.
        current_time = self.get_current_time()
        events = [
            (current_time - 4000, "A", 10, 1),
            (current_time - 3000, "A", 30, 2),
            (current_time - 2000, "A", 20, 3)
        ]
        for event in events:
            self.aggregator.add_event(event)
        median = self.aggregator.get_median("A", current_time)
        # For three values 10,30,20 the sorted order is 10,20,30 and median is 20.
        self.assertEqual(median, 20, "Median should be the middle value for odd count events")

    def test_multiple_events_even_count(self):
        # For even count, the median can be defined as the average of the two middle values.
        # Since the aggregator calculates an approximate median, allow a small relative error.
        current_time = self.get_current_time()
        events = [
            (current_time - 4500, "B", 10, 1),
            (current_time - 3500, "B", 30, 2),
            (current_time - 2500, "B", 20, 3),
            (current_time - 1500, "B", 40, 4)
        ]
        for event in events:
            self.aggregator.add_event(event)
        median = self.aggregator.get_median("B", current_time)
        # True median is (20+30)/2 = 25. Allow small deviation within error_bound.
        expected = 25
        self.assertAlmostEqual(median, expected, delta=expected * self.error_bound,
            msg="Approximate median for even number of events should be within the allowed error")
 
    def test_out_of_order_events(self):
        # Insert events out of order and verify that the aggregator processes them correctly.
        current_time = self.get_current_time()
        events = [
            (current_time - 2000, "C", 15, 1),
            (current_time - 4000, "C", 5, 2),
            (current_time - 3000, "C", 10, 3)
        ]
        # Add events in a shuffled order.
        for event in sorted(events, key=lambda e: e[0], reverse=True):
            self.aggregator.add_event(event)
        median = self.aggregator.get_median("C", current_time)
        # Sorted values: [5, 10, 15]. Median is 10.
        self.assertEqual(median, 10, "Aggregator should correctly compute the median even with out-of-order events")

    def test_sliding_window_filtering(self):
        # Events that are outside the sliding window should be ignored.
        current_time = self.get_current_time()
        # Event within window: timestamp = current_time - 1000
        event_in = (current_time - 1000, "D", 100, 1)
        # Event outside window: timestamp = current_time - 6000 (window is 5000)
        event_out = (current_time - 6000, "D", 200, 2)
        self.aggregator.add_event(event_in)
        self.aggregator.add_event(event_out)
        median = self.aggregator.get_median("D", current_time)
        # Only event_in is within the window, so median should be 100.
        self.assertEqual(median, 100, "Events outside the sliding window should be discarded")

    def test_duplicate_events(self):
        # Duplicate events should be handled gracefully; they may be processed as separate events
        # or deduplicated based on the implementation.
        current_time = self.get_current_time()
        event = (current_time - 1500, "E", 50, 1)
        # Add the same event twice.
        self.aggregator.add_event(event)
        self.aggregator.add_event(event)
        median = self.aggregator.get_median("E", current_time)
        # If duplicates are processed, the median of [50, 50] is still 50.
        self.assertEqual(median, 50, "Duplicate events should not affect the median calculation")

    def test_multiple_categories(self):
        current_time = self.get_current_time()
        events = [
            (current_time - 1000, "F", 5, 1),
            (current_time - 1200, "F", 15, 2),
            (current_time - 1000, "G", 20, 3),
            (current_time - 800,  "G", 30, 4)
        ]
        for event in events:
            self.aggregator.add_event(event)
        median_F = self.aggregator.get_median("F", current_time)
        median_G = self.aggregator.get_median("G", current_time)
        # For category F, median of [5,15] is 10 (average)
        expected_F = 10
        # For category G, median of [20,30] is 25 (average)
        expected_G = 25
        self.assertAlmostEqual(median_F, expected_F, delta=expected_F * self.error_bound,
            msg="Median for category F should be within allowed error")
        self.assertAlmostEqual(median_G, expected_G, delta=expected_G * self.error_bound,
            msg="Median for category G should be within allowed error")

    def test_late_events(self):
        # Late events (ones that fall into an older window) should be discarded.
        current_time = self.get_current_time()
        # Add an event that is within the window
        event_recent = (current_time - 500, "H", 60, 1)
        # Add a late event that is older than the sliding window
        event_late = (current_time - 7000, "H", 100, 2)
        self.aggregator.add_event(event_recent)
        self.aggregator.add_event(event_late)
        median = self.aggregator.get_median("H", current_time)
        # Only the recent event should be considered.
        self.assertEqual(median, 60, "Late events should be excluded from the median calculation")

if __name__ == '__main__':
    unittest.main()