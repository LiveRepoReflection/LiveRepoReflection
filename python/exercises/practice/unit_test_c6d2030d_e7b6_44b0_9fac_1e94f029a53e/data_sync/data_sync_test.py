import unittest
from data_sync import optimize_sync

class DataSyncTest(unittest.TestCase):
    def test_simple_two_nodes(self):
        N, M = 2, 1
        data_sources = [{"A": 1}, {}]
        network_latency = [[0.0, 1.0], [1.0, 0.0]]
        reliability = [1.0, 1.0]
        updates = [("A", 2, 0)]
        
        result = optimize_sync(N, M, data_sources, network_latency, reliability, updates)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (0, 1, "A", 2))

    def test_three_nodes_with_reliability(self):
        N, M = 3, 2
        data_sources = [{"A": 1, "B": 2}, {"A": 1}, {"B": 2}]
        network_latency = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.0],
            [2.0, 1.0, 0.0]
        ]
        reliability = [0.9, 1.0, 0.8]
        updates = [("A", 3, 0), ("B", 4, 2)]
        
        result = optimize_sync(N, M, data_sources, network_latency, reliability, updates)
        
        # Verify all propagations are valid
        for src, dst, key, value in result:
            self.assertTrue(0 <= src < N)
            self.assertTrue(0 <= dst < N)
            self.assertTrue(key in ["A", "B"])
            self.assertTrue(value in [3, 4])

    def test_unreliable_node(self):
        N, M = 3, 1
        data_sources = [{"A": 1}, {"A": 1}, {"A": 1}]
        network_latency = [
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 0.0]
        ]
        reliability = [1.0, 0.0, 1.0]  # Node 1 is completely unreliable
        updates = [("A", 2, 0)]
        
        result = optimize_sync(N, M, data_sources, network_latency, reliability, updates)
        
        # Verify no propagations to unreliable node
        for src, dst, key, value in result:
            self.assertNotEqual(dst, 1)

    def test_disconnected_nodes(self):
        N, M = 3, 1
        data_sources = [{"A": 1}, {"A": 1}, {"A": 1}]
        network_latency = [
            [0.0, float('inf'), 1.0],
            [float('inf'), 0.0, float('inf')],
            [1.0, float('inf'), 0.0]
        ]
        reliability = [1.0, 1.0, 1.0]
        updates = [("A", 2, 0)]
        
        result = optimize_sync(N, M, data_sources, network_latency, reliability, updates)
        
        # Verify no impossible propagations
        for src, dst, key, value in result:
            self.assertNotEqual(network_latency[src][dst], float('inf'))

    def test_empty_updates(self):
        N, M = 2, 1
        data_sources = [{"A": 1}, {"A": 1}]
        network_latency = [[0.0, 1.0], [1.0, 0.0]]
        reliability = [1.0, 1.0]
        updates = []
        
        result = optimize_sync(N, M, data_sources, network_latency, reliability, updates)
        
        self.assertEqual(len(result), 0)

    def test_multiple_updates_same_key(self):
        N, M = 2, 1
        data_sources = [{"A": 1}, {"A": 1}]
        network_latency = [[0.0, 1.0], [1.0, 0.0]]
        reliability = [1.0, 1.0]
        updates = [("A", 2, 0), ("A", 3, 1), ("A", 4, 0)]
        
        result = optimize_sync(N, M, data_sources, network_latency, reliability, updates)
        
        # Verify final value is propagated
        final_value = None
        for src, dst, key, value in result:
            if key == "A":
                final_value = value
        self.assertEqual(final_value, 4)

    def test_large_scale(self):
        N, M = 5, 3
        data_sources = [
            {"A": 1, "B": 2, "C": 3},
            {"A": 1},
            {"B": 2},
            {"C": 3},
            {}
        ]
        network_latency = [
            [0.0, 1.0, 2.0, 3.0, 4.0],
            [1.0, 0.0, 1.0, 2.0, 3.0],
            [2.0, 1.0, 0.0, 1.0, 2.0],
            [3.0, 2.0, 1.0, 0.0, 1.0],
            [4.0, 3.0, 2.0, 1.0, 0.0]
        ]
        reliability = [0.9, 0.8, 0.7, 0.6, 0.5]
        updates = [
            ("A", 10, 0),
            ("B", 20, 2),
            ("C", 30, 3)
        ]
        
        result = optimize_sync(N, M, data_sources, network_latency, reliability, updates)
        
        # Basic validation of result structure
        self.assertTrue(len(result) > 0)
        for src, dst, key, value in result:
            self.assertTrue(0 <= src < N)
            self.assertTrue(0 <= dst < N)
            self.assertTrue(key in ["A", "B", "C"])
            self.assertTrue(value in [10, 20, 30])

if __name__ == '__main__':
    unittest.main()