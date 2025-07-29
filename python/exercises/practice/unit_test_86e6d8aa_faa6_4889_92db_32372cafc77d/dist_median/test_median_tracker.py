import unittest
import random
from dist_median.median_tracker import MedianTracker

class TestMedianTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = MedianTracker()
        self.node_ids = ['node1', 'node2', 'node3', 'node4']
        
    def test_single_node_single_value(self):
        self.tracker.add_value('node1', 5)
        self.assertEqual(self.tracker.estimate_median(), 5.0)
        
    def test_single_node_multiple_values(self):
        for val in [1, 2, 3, 4, 5]:
            self.tracker.add_value('node1', val)
        self.assertEqual(self.tracker.estimate_median(), 3.0)
        
    def test_multiple_nodes_even_distribution(self):
        for i, val in enumerate([1, 3, 5, 7, 9, 2, 4, 6, 8, 10]):
            node_id = self.node_ids[i % len(self.node_ids)]
            self.tracker.add_value(node_id, val)
        median = self.tracker.estimate_median()
        self.assertTrue(4.5 <= median <= 6.5)
        
    def test_multiple_nodes_skewed_distribution(self):
        # Node1 gets most of the low values
        for val in range(1, 101):
            self.tracker.add_value('node1', val)
        # Other nodes get few high values
        for val in [1000, 2000, 3000]:
            self.tracker.add_value('node2', val)
        median = self.tracker.estimate_median()
        self.assertTrue(45 <= median <= 55)
        
    def test_large_dataset(self):
        random.seed(42)
        for _ in range(1000):
            node_id = random.choice(self.node_ids)
            val = random.randint(1, 1000)
            self.tracker.add_value(node_id, val)
        true_median = 500.5  # Expected for uniform distribution
        estimated = self.tracker.estimate_median()
        self.assertTrue(0.95 * true_median <= estimated <= 1.05 * true_median)
        
    def test_empty_data(self):
        with self.assertRaises(ValueError):
            self.tracker.estimate_median()
            
    def test_negative_values(self):
        for val in [-5, -3, -1, 0, 2, 4, 6]:
            self.tracker.add_value('node1', val)
        median = self.tracker.estimate_median()
        self.assertEqual(median, 0.0)
        
    def test_duplicate_values(self):
        for _ in range(10):
            for val in [5, 5, 5, 10, 10]:
                self.tracker.add_value('node1', val)
        median = self.tracker.estimate_median()
        self.assertEqual(median, 5.0)

if __name__ == '__main__':
    unittest.main()