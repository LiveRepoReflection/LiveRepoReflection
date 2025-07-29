import unittest
from influence_max import select_seeds

class TestInfluenceMax(unittest.TestCase):
    def test_small_network(self):
        n = 5
        edges = [(0, 1, 0.8), (0, 2, 0.5), (1, 3, 0.9), (2, 4, 0.6)]
        k = 2
        iterations = 3
        threshold = 0.7
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), k)
        self.assertTrue(all(0 <= seed < n for seed in seeds))

    def test_disconnected_graph(self):
        n = 4
        edges = [(0, 1, 0.9), (2, 3, 0.8)]
        k = 2
        iterations = 2
        threshold = 0.5
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), k)
        self.assertTrue(all(0 <= seed < n for seed in seeds))

    def test_no_edges(self):
        n = 3
        edges = []
        k = 1
        iterations = 1
        threshold = 0.1
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), k)
        self.assertTrue(all(0 <= seed < n for seed in seeds))

    def test_max_seeds(self):
        n = 4
        edges = [(0, 1, 0.5), (1, 2, 0.5), (2, 3, 0.5)]
        k = 4
        iterations = 1
        threshold = 0.1
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), k)
        self.assertEqual(set(seeds), set(range(n)))

    def test_zero_seeds(self):
        n = 3
        edges = [(0, 1, 0.9), (1, 2, 0.9)]
        k = 0
        iterations = 2
        threshold = 0.5
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), 0)

    def test_high_threshold(self):
        n = 3
        edges = [(0, 1, 0.6), (0, 2, 0.6)]
        k = 1
        iterations = 2
        threshold = 1.0
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), k)
        self.assertTrue(0 <= seeds[0] < n)

    def test_cycle_network(self):
        n = 4
        edges = [(0, 1, 0.7), (1, 2, 0.7), (2, 3, 0.7), (3, 0, 0.7)]
        k = 1
        iterations = 3
        threshold = 0.6
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), k)
        self.assertTrue(0 <= seeds[0] < n)

    def test_large_network(self):
        n = 100
        edges = [(i, (i+1)%n, 0.5) for i in range(n)]
        k = 10
        iterations = 5
        threshold = 0.3
        seeds = select_seeds(n, edges, k, iterations, threshold)
        self.assertEqual(len(seeds), k)
        self.assertTrue(all(0 <= seed < n for seed in seeds))

if __name__ == '__main__':
    unittest.main()