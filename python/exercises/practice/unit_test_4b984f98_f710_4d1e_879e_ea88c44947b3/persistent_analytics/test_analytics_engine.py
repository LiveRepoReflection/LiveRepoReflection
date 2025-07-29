import unittest
import os
import tempfile
import shutil
import time
from persistent_analytics import AnalyticsEngine

class TestAnalyticsEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'analytics.db')
        self.engine = AnalyticsEngine(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_record_event(self):
        self.engine.record_event(1, "click", 1000, {"value": 5})
        self.engine.record_event(2, "view", 1001, {"value": 3})
        self.engine.record_event(1, "click", 1002, {"value": 7})

        # Test event count
        result = self.engine.get_aggregate("event_count", 10, 1000, 1010)
        self.assertEqual(result, 3)

    def test_unique_users(self):
        self.engine.record_event(1, "click", 1000, {})
        self.engine.record_event(2, "view", 1001, {})
        self.engine.record_event(1, "click", 1002, {})

        result = self.engine.get_aggregate("unique_users", 10, 1000, 1010)
        self.assertEqual(result, 2)

    def test_average_data_value(self):
        self.engine.record_event(1, "click", 1000, {"value": 5})
        self.engine.record_event(2, "view", 1001, {"value": 3})
        self.engine.record_event(3, "click", 1002, {})  # No value field
        self.engine.record_event(4, "click", 1003, {"value": 7})

        result = self.engine.get_aggregate("average_data_value", 10, 1000, 1010, "value")
        self.assertAlmostEqual(result, (5 + 3 + 7) / 3)

    def test_time_windows(self):
        for i in range(10):
            self.engine.record_event(1, "click", 1000 + i, {"value": i})

        # Test different window sizes
        self.assertEqual(self.engine.get_aggregate("event_count", 5, 1000, 1009), 10)
        self.assertEqual(self.engine.get_aggregate("event_count", 3, 1000, 1009), 10)
        self.assertEqual(self.engine.get_aggregate("event_count", 1, 1000, 1009), 10)

    def test_persistence(self):
        # Record some events
        self.engine.record_event(1, "click", 1000, {"value": 5})
        self.engine.record_event(2, "view", 1001, {"value": 3})
        self.engine.save_data()

        # Create new engine instance and load data
        new_engine = AnalyticsEngine(self.db_path)
        new_engine.load_data()

        # Verify data was persisted
        result = new_engine.get_aggregate("event_count", 10, 1000, 1010)
        self.assertEqual(result, 2)

    def test_data_expiration(self):
        now = int(time.time())
        thirty_days_ago = now - (30 * 24 * 3600)
        one_day_after_expiry = thirty_days_ago - 86400

        # Record events that should be kept and expired
        self.engine.record_event(1, "click", thirty_days_ago, {})
        self.engine.record_event(2, "view", now, {})
        self.engine.record_event(3, "click", one_day_after_expiry, {})

        # Force cleanup
        self.engine.cleanup_expired_events()

        # Verify only recent events are kept
        result = self.engine.get_aggregate("event_count", 30 * 24 * 3600, thirty_days_ago, now)
        self.assertEqual(result, 2)

    def test_edge_cases(self):
        # Empty time window
        result = self.engine.get_aggregate("event_count", 10, 2000, 2010)
        self.assertEqual(result, 0)

        # Single event in window
        self.engine.record_event(1, "click", 1000, {"value": 5})
        result = self.engine.get_aggregate("event_count", 1, 1000, 1000)
        self.assertEqual(result, 1)

        # Non-existent field in average calculation
        self.engine.record_event(1, "click", 1000, {})
        result = self.engine.get_aggregate("average_data_value", 10, 1000, 1010, "nonexistent")
        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()