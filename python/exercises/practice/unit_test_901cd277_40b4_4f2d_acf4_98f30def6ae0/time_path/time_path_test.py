import unittest
from time_path import find_min_time

class TestTimePath(unittest.TestCase):
    def test_single_source_single_path(self):
        n = 3
        edges = [
            (0, 1, [1]*24),
            (1, 2, [1]*24)
        ]
        sources = [0]
        destination = 2
        start_time = 0
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), 2)

    def test_multi_source_shortest_path(self):
        n = 4
        edges = [
            (0, 2, [5]*24),
            (1, 2, [1]*24),
            (2, 3, [1]*24)
        ]
        sources = [0, 1]
        destination = 3
        start_time = 0
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), 2)

    def test_time_dependent_costs(self):
        n = 3
        edges = [
            (0, 1, [10 if h < 12 else 1 for h in range(24)]),
            (1, 2, [1]*24)
        ]
        sources = [0]
        destination = 2
        start_time = 12  # Should take cheaper path
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), 2)

    def test_no_path_exists(self):
        n = 4
        edges = [
            (0, 1, [1]*24),
            (2, 3, [1]*24)
        ]
        sources = [0]
        destination = 3
        start_time = 0
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), -1)

    def test_large_time_wrap(self):
        n = 3
        edges = [
            (0, 1, [23]*24),
            (1, 2, [2]*24)
        ]
        sources = [0]
        destination = 2
        start_time = 23  # Should wrap around midnight
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), 25)

    def test_cyclic_graph(self):
        n = 3
        edges = [
            (0, 1, [1]*24),
            (1, 2, [1]*24),
            (2, 0, [1]*24)
        ]
        sources = [0]
        destination = 2
        start_time = 0
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), 2)

    def test_multiple_paths_different_times(self):
        n = 4
        edges = [
            (0, 1, [1]*24),
            (0, 2, [3]*24),
            (1, 3, [3]*24),
            (2, 3, [1]*24)
        ]
        sources = [0]
        destination = 3
        start_time = 0
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), 4)

    def test_varying_hourly_costs(self):
        n = 3
        edges = [
            (0, 1, [h for h in range(24)]),  # More expensive as hour increases
            (1, 2, [1]*24)
        ]
        sources = [0]
        destination = 2
        start_time = 0  # Should take path immediately at hour 0
        self.assertEqual(find_min_time(n, edges, sources, destination, start_time), 1)

if __name__ == '__main__':
    unittest.main()