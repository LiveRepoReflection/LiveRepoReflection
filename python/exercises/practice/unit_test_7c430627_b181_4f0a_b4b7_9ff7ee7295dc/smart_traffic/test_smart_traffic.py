import unittest
from smart_traffic import SmartTrafficRouter

class TestSmartTraffic(unittest.TestCase):
    def setUp(self):
        self.edges = [
            (0, 1, 10, 50),
            (0, 2, 5, 20),
            (1, 2, 3, 10),
            (1, 3, 7, 30),
            (2, 3, 2, 5),
        ]
        self.router = SmartTrafficRouter(self.edges)

    def test_shortest_path(self):
        requests = [(0, 3, "shortest")]
        expected = [[0, 2, 3]]
        results = self.router.process_requests(requests)
        self.assertEqual(results, expected)

    def test_least_congestion_path(self):
        requests = [(0, 3, "least_congestion")]
        expected = [[0, 2, 3]]
        results = self.router.process_requests(requests)
        self.assertEqual(results, expected)

    def test_balanced_path(self):
        requests = [(0, 3, "balanced")]
        expected = [[0, 2, 3]]
        results = self.router.process_requests(requests)
        self.assertEqual(results, expected)

    def test_traffic_update(self):
        self.router.update_traffic(4, 100)  # Increase traffic on edge (2,3)
        requests = [(0, 3, "least_congestion")]
        expected = [[0, 1, 3]]
        results = self.router.process_requests(requests)
        self.assertEqual(results, expected)

    def test_no_path_exists(self):
        edges = [(0, 1, 10, 50), (2, 3, 5, 20)]
        router = SmartTrafficRouter(edges)
        requests = [(0, 3, "shortest")]
        expected = [[]]
        results = router.process_requests(requests)
        self.assertEqual(results, expected)

    def test_multiple_requests(self):
        requests = [
            (0, 3, "shortest"),
            (0, 3, "least_congestion"),
            (0, 3, "balanced")
        ]
        expected = [
            [0, 2, 3],
            [0, 2, 3],
            [0, 2, 3]
        ]
        results = self.router.process_requests(requests)
        self.assertEqual(results, expected)

    def test_invalid_preference(self):
        requests = [(0, 3, "invalid")]
        with self.assertRaises(ValueError):
            self.router.process_requests(requests)

    def test_empty_requests(self):
        requests = []
        expected = []
        results = self.router.process_requests(requests)
        self.assertEqual(results, expected)

    def test_single_node_path(self):
        requests = [(0, 0, "shortest")]
        expected = [[0]]
        results = self.router.process_requests(requests)
        self.assertEqual(results, expected)

if __name__ == '__main__':
    unittest.main()