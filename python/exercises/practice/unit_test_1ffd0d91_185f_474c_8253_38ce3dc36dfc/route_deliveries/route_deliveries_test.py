import unittest
from route_deliveries import route_deliveries

class TestRouteDeliveries(unittest.TestCase):
    def test_sample_scenario(self):
        graph = {
            0: [(1, 5), (2, 3)],
            1: [(3, 6)],
            2: [(1, 2), (3, 4)],
            3: []
        }
        packages = [
            (0, 3, 12),  # Shortest path 0 -> 2 -> 3 with total cost 7 (or 0->1->3 with cost 11)
            (2, 3, 6),   # Shortest path 2 -> 3 with cost 4
            (0, 1, 6)    # Direct path 0 -> 1 with cost 5
        ]
        expected = 3
        self.assertEqual(route_deliveries(graph, packages), expected)

    def test_no_valid_path(self):
        graph = {
            0: [(1, 2)],
            1: []
        }
        packages = [
            (0, 1, 1),   # Cost is 2, deadline is 1, not deliverable
            (0, 1, 3)    # Cost is 2, deadline is 3, deliverable
        ]
        expected = 1
        self.assertEqual(route_deliveries(graph, packages), expected)

    def test_cycle_graph(self):
        # Graph with cycle: 0 -> 1 -> 2 -> 0.
        graph = {
            0: [(1, 1)],
            1: [(2, 1)],
            2: [(0, 1)]
        }
        packages = [
            (0, 2, 3),   # Shortest path 0 -> 1 -> 2 with cost 2, deliverable
            (0, 2, 2)    # Shortest path equals deadline, deliverable
        ]
        expected = 2
        self.assertEqual(route_deliveries(graph, packages), expected)

    def test_multiple_paths(self):
        # Graph with multiple possible routes:
        # 0 -> 1 (2), 0 -> 2 (4), 1 -> 3 (3), 2 -> 3 (1)
        graph = {
            0: [(1, 2), (2, 4)],
            1: [(3, 3)],
            2: [(3, 1)],
            3: []
        }
        packages = [
            (0, 3, 5),  # Shortest path: 0->1->3 or 0->2->3, cost = 5
            (0, 3, 6)   # Both routes deliverable
        ]
        expected = 2
        self.assertEqual(route_deliveries(graph, packages), expected)

    def test_origin_equals_destination(self):
        # When origin and destination are the same, delivery requires no travel.
        graph = {
            0: []
        }
        packages = [
            (0, 0, 0),
            (0, 0, 5)
        ]
        expected = 2
        self.assertEqual(route_deliveries(graph, packages), expected)

if __name__ == '__main__':
    unittest.main()