import unittest
from time_series_store import TimeSeriesStore

class TestTimeSeriesStore(unittest.TestCase):
    def setUp(self):
        self.store = TimeSeriesStore()

    def test_set_and_get_basic(self):
        self.store.set("temp", 25, 1000)
        self.assertEqual(self.store.get("temp", 1000), 25)
        self.assertEqual(self.store.get("temp", 1001), 25)
        self.assertEqual(self.store.get("temp", 999), -1)

    def test_get_with_multiple_timestamps(self):
        self.store.set("temp", 25, 1000)
        self.store.set("temp", 26, 1005)
        self.store.set("temp", 27, 1010)
        self.assertEqual(self.store.get("temp", 1004), 25)
        self.assertEqual(self.store.get("temp", 1005), 26)
        self.assertEqual(self.store.get("temp", 1009), 26)
        self.assertEqual(self.store.get("temp", 1010), 27)

    def test_get_nonexistent_key(self):
        self.assertEqual(self.store.get("nonexistent", 1000), -1)

    def test_aggregate_sum(self):
        self.store.set("temp", 10, 1000)
        self.store.set("temp", 20, 1005)
        self.store.set("temp", 30, 1010)
        self.assertEqual(self.store.aggregate("temp", 1000, 1010, "SUM"), 60)
        self.assertEqual(self.store.aggregate("temp", 1001, 1009, "SUM"), 20)
        self.assertEqual(self.store.aggregate("temp", 999, 999, "SUM"), 0)

    def test_aggregate_avg(self):
        self.store.set("temp", 10, 1000)
        self.store.set("temp", 20, 1005)
        self.store.set("temp", 30, 1010)
        self.assertEqual(self.store.aggregate("temp", 1000, 1010, "AVG"), 20)
        self.assertEqual(self.store.aggregate("temp", 1001, 1009, "AVG"), 20)
        self.assertEqual(self.store.aggregate("temp", 999, 999, "AVG"), 0)

    def test_aggregate_max(self):
        self.store.set("temp", 10, 1000)
        self.store.set("temp", 20, 1005)
        self.store.set("temp", 30, 1010)
        self.assertEqual(self.store.aggregate("temp", 1000, 1010, "MAX"), 30)
        self.assertEqual(self.store.aggregate("temp", 1001, 1009, "MAX"), 20)
        self.assertEqual(self.store.aggregate("temp", 999, 999, "MAX"), -1)

    def test_aggregate_min(self):
        self.store.set("temp", 10, 1000)
        self.store.set("temp", 20, 1005)
        self.store.set("temp", 30, 1010)
        self.assertEqual(self.store.aggregate("temp", 1000, 1010, "MIN"), 10)
        self.assertEqual(self.store.aggregate("temp", 1001, 1009, "MIN"), 20)
        self.assertEqual(self.store.aggregate("temp", 999, 999, "MIN"), -1)

    def test_multiple_keys(self):
        self.store.set("temp", 25, 1000)
        self.store.set("humidity", 50, 1000)
        self.assertEqual(self.store.get("temp", 1000), 25)
        self.assertEqual(self.store.get("humidity", 1000), 50)
        self.assertEqual(self.store.aggregate("temp", 1000, 1000, "SUM"), 25)
        self.assertEqual(self.store.aggregate("humidity", 1000, 1000, "SUM"), 50)

    def test_large_timestamps(self):
        self.store.set("data", 42, 10**9)
        self.assertEqual(self.store.get("data", 10**9 + 1), 42)
        self.assertEqual(self.store.aggregate("data", 10**9, 10**9, "SUM"), 42)

    def test_empty_range_aggregations(self):
        self.store.set("temp", 25, 1000)
        self.assertEqual(self.store.aggregate("temp", 2000, 3000, "SUM"), 0)
        self.assertEqual(self.store.aggregate("temp", 2000, 3000, "AVG"), 0)
        self.assertEqual(self.store.aggregate("temp", 2000, 3000, "MAX"), -1)
        self.assertEqual(self.store.aggregate("temp", 2000, 3000, "MIN"), -1)

    def test_negative_values(self):
        self.store.set("temp", -10, 1000)
        self.store.set("temp", -20, 1005)
        self.assertEqual(self.store.get("temp", 1005), -20)
        self.assertEqual(self.store.aggregate("temp", 1000, 1005, "SUM"), -30)
        self.assertEqual(self.store.aggregate("temp", 1000, 1005, "AVG"), -15)
        self.assertEqual(self.store.aggregate("temp", 1000, 1005, "MAX"), -10)
        self.assertEqual(self.store.aggregate("temp", 1000, 1005, "MIN"), -20)

if __name__ == '__main__':
    unittest.main()