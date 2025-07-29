import unittest
from adaptive_router import adaptive_router

class TestAdaptiveRouter(unittest.TestCase):
    def test_small_network(self):
        N = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 2), (1, 3, 7), (2, 3, 1)]
        requests = [(0, 3, 5), (1, 3, 3)]
        initial_load = {
            (0, 1): 0, (1, 0): 0,
            (0, 2): 0, (2, 0): 0,
            (1, 2): 0, (2, 1): 0,
            (1, 3): 0, (3, 1): 0,
            (2, 3): 0, (3, 2): 0
        }
        result = adaptive_router(N, edges, requests, initial_load)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 0)
        self.assertEqual(result[0][-1], 3)
        self.assertEqual(result[1][0], 1)
        self.assertEqual(result[1][-1], 3)

    def test_no_path_available(self):
        N = 3
        edges = [(0, 1, 10)]
        requests = [(0, 2, 5), (1, 2, 3)]
        initial_load = {(0, 1): 0, (1, 0): 0}
        result = adaptive_router(N, edges, requests, initial_load)
        self.assertEqual(result, [None, None])

    def test_heavy_congestion(self):
        N = 3
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 5)]
        requests = [(0, 2, 10), (0, 2, 5), (1, 2, 5)]
        initial_load = {
            (0, 1): 8, (1, 0): 8,
            (0, 2): 4, (2, 0): 4,
            (1, 2): 4, (2, 1): 4
        }
        result = adaptive_router(N, edges, requests, initial_load)
        self.assertEqual(len(result), 3)
        for path in result:
            if path is not None:
                self.assertEqual(path[0] in {0, 1}, True)
                self.assertEqual(path[-1], 2)

    def test_large_network(self):
        N = 10
        edges = [
            (0, 1, 10), (1, 2, 10), (2, 3, 10), (3, 4, 10),
            (4, 5, 10), (5, 6, 10), (6, 7, 10), (7, 8, 10),
            (8, 9, 10), (0, 9, 100)
        ]
        requests = [(0, 9, 5), (1, 8, 5), (2, 7, 5)]
        initial_load = {(u, v): 0 for u, v, _ in edges}
        initial_load.update({(v, u): 0 for u, v, _ in edges})
        result = adaptive_router(N, edges, requests, initial_load)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], [0, 9])
        self.assertEqual(result[1][0], 1)
        self.assertEqual(result[1][-1], 8)
        self.assertEqual(result[2][0], 2)
        self.assertEqual(result[2][-1], 7)

    def test_tie_breaking(self):
        N = 3
        edges = [(0, 1, 10), (0, 2, 10), (1, 2, 10)]
        requests = [(0, 2, 1)]
        initial_load = {
            (0, 1): 0, (1, 0): 0,
            (0, 2): 0, (2, 0): 0,
            (1, 2): 0, (2, 1): 0
        }
        result = adaptive_router(N, edges, requests, initial_load)
        self.assertEqual(result[0], [0, 2])

if __name__ == '__main__':
    unittest.main()