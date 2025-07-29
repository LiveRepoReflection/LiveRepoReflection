import unittest
from distributed_median import DistributedMedian

class TestDistributedMedian(unittest.TestCase):
    def setUp(self):
        self.dm = DistributedMedian()

    def test_local_median_single_shard_odd(self):
        # Test local median for a single shard with an odd number of elements.
        shard = "shard1"
        values = [10, 20, 30]
        for value in values:
            self.dm.ingest(shard, value)
        # Sorted values: [10, 20, 30] => median should be 20.
        self.assertEqual(self.dm.get_local_median(shard), 20)

    def test_local_median_single_shard_even(self):
        # Test local median for a single shard with an even number of elements.
        shard = "shard1"
        values = [5, 15]
        for value in values:
            self.dm.ingest(shard, value)
        # Sorted values: [5, 15] => median should be (5 + 15) / 2 = 10.
        self.assertEqual(self.dm.get_local_median(shard), 10)

    def test_global_median_single_shard(self):
        # Test global median when only one shard exists.
        shard = "shard1"
        values = [7, 3, 5, 9, 11]
        for value in values:
            self.dm.ingest(shard, value)
        # Sorted values: [3, 5, 7, 9, 11] => median is 7.
        self.assertEqual(self.dm.get_global_median(), 7)

    def test_global_median_multiple_shards(self):
        # Test global median with data from two shards.
        shard1 = "shard1"
        shard2 = "shard2"
        values1 = [1, 3, 5]
        values2 = [2, 4, 6]
        for value in values1:
            self.dm.ingest(shard1, value)
        for value in values2:
            self.dm.ingest(shard2, value)
        # Merged sorted values: [1, 2, 3, 4, 5, 6] => median is (3 + 4) / 2 = 3.5.
        self.assertEqual(self.dm.get_global_median(), 3.5)

    def test_global_median_mixed_distributions(self):
        # Test global median with data from multiple shards having different distributions.
        shard_a = "A"
        shard_b = "B"
        shard_c = "C"
        values_a = [100, 50, 75]
        values_b = [20, 40, 60, 80]
        values_c = [10, 30, 90]
        for value in values_a:
            self.dm.ingest(shard_a, value)
        for value in values_b:
            self.dm.ingest(shard_b, value)
        for value in values_c:
            self.dm.ingest(shard_c, value)
        # Merged sorted values: [10, 20, 30, 40, 50, 60, 75, 80, 90, 100]
        # Even count => median is (50 + 60) / 2 = 55.
        self.assertEqual(self.dm.get_global_median(), 55)

    def test_empty_global_median(self):
        # Test that calling global median without any data raises a ValueError.
        with self.assertRaises(ValueError):
            self.dm.get_global_median()

    def test_empty_local_median(self):
        # Test that calling local median for a shard with no data raises a ValueError.
        with self.assertRaises(ValueError):
            self.dm.get_local_median("non_existing_shard")

    def test_order_independence(self):
        # Test that ingestion order does not affect the computed median.
        shard = "shard1"
        values = [5, 1, 3, 2, 4]
        for value in values:
            self.dm.ingest(shard, value)
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 1:
            expected_median = sorted_values[n // 2]
        else:
            expected_median = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        self.assertEqual(self.dm.get_local_median(shard), expected_median)
        self.assertEqual(self.dm.get_global_median(), expected_median)

if __name__ == "__main__":
    unittest.main()