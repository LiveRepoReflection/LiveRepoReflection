import unittest
from island_hopping import island_hopping

class TestIslandHopping(unittest.TestCase):
    def test_single_source_single_target(self):
        n = 3
        edges = [(0, 1, 2), (1, 2, 3)]
        sources = [0]
        targets = [2]
        k = 3
        self.assertEqual(island_hopping(n, edges, sources, targets, k), 5)

    def test_multiple_sources_multiple_targets(self):
        n = 5
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 2), (1, 3, 1), (2, 4, 7), (3, 4, 3)]
        sources = [0, 1]
        targets = [3, 4]
        k = 4
        self.assertEqual(island_hopping(n, edges, sources, targets, k), 1)

    def test_no_path_exists(self):
        n = 4
        edges = [(0, 1, 1), (2, 3, 2)]
        sources = [0]
        targets = [3]
        k = 3
        self.assertEqual(island_hopping(n, edges, sources, targets, k), -1)

    def test_source_is_target(self):
        n = 3
        edges = [(0, 1, 2), (1, 2, 3)]
        sources = [1]
        targets = [1]
        k = 1
        self.assertEqual(island_hopping(n, edges, sources, targets, k), 0)

    def test_k_too_small(self):
        n = 4
        edges = [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
        sources = [0]
        targets = [3]
        k = 2
        self.assertEqual(island_hopping(n, edges, sources, targets, k), -1)

    def test_large_k_value(self):
        n = 4
        edges = [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
        sources = [0]
        targets = [3]
        k = 10
        self.assertEqual(island_hopping(n, edges, sources, targets, k), 3)

    def test_empty_sources(self):
        n = 3
        edges = [(0, 1, 1), (1, 2, 1)]
        sources = []
        targets = [2]
        k = 3
        self.assertEqual(island_hopping(n, edges, sources, targets, k), -1)

    def test_empty_targets(self):
        n = 3
        edges = [(0, 1, 1), (1, 2, 1)]
        sources = [0]
        targets = []
        k = 3
        self.assertEqual(island_hopping(n, edges, sources, targets, k), -1)

    def test_cycle_in_graph(self):
        n = 3
        edges = [(0, 1, 1), (1, 2, 1), (2, 0, 1)]
        sources = [0]
        targets = [2]
        k = 3
        self.assertEqual(island_hopping(n, edges, sources, targets, k), 1)

    def test_multiple_paths_with_different_costs(self):
        n = 4
        edges = [(0, 1, 1), (0, 2, 5), (1, 3, 1), (2, 3, 1)]
        sources = [0]
        targets = [3]
        k = 3
        self.assertEqual(island_hopping(n, edges, sources, targets, k), 2)

if __name__ == '__main__':
    unittest.main()