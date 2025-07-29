import unittest
from highway_patrol import optimal_patrol_placement

class TestHighwayPatrol(unittest.TestCase):
    def test_all_patrolled_example(self):
        n = 4
        k = 2
        edges = [
            (0, 1, 10, 5),  # expected accidents on edge = 10*5 when unpatrolled
            (1, 2, 15, 3),
            (2, 3, 5, 8),
            (0, 3, 20, 2)
        ]
        # Placing patrols at appropriate cities can reduce unpatrolled accidents to 0.
        result = optimal_patrol_placement(n, k, edges)
        self.assertEqual(result, 0)

    def test_single_patrol_unit_example(self):
        n = 5
        k = 1
        edges = [
            (0, 1, 10, 5),
            (1, 2, 15, 3),
            (2, 3, 5, 8),
            (0, 3, 20, 2),
            (3, 4, 7, 4)
        ]
        # Based on analysis, the optimal placement yields an unpatrolled accident count of 95.
        result = optimal_patrol_placement(n, k, edges)
        self.assertEqual(result, 95)

    def test_no_patrol_units(self):
        n = 3
        k = 0
        edges = [
            (0, 1, 10, 5),
            (1, 2, 15, 3),
            (0, 2, 20, 4)
        ]
        # With no patrols, every edge is unpatrolled.
        total = sum(l * r for _, _, l, r in edges)
        result = optimal_patrol_placement(n, k, edges)
        self.assertEqual(result, total)

    def test_all_patrol_units(self):
        n = 3
        k = 3
        edges = [
            (0, 1, 10, 5),
            (1, 2, 15, 3),
            (0, 2, 20, 4)
        ]
        # With patrols at every city, all edges are patrolled.
        result = optimal_patrol_placement(n, k, edges)
        self.assertEqual(result, 0)

    def test_random_small_case(self):
        n = 6
        k = 2
        edges = [
            (0, 1, 5, 2),
            (0, 2, 10, 3),
            (1, 2, 7, 1),
            (1, 3, 8, 4),
            (2, 4, 6, 2),
            (3, 4, 12, 3),
            (3, 5, 10, 1),
            (4, 5, 5, 2)
        ]
        # We test basic invariants: result must be an integer and non-negative.
        result = optimal_patrol_placement(n, k, edges)
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

    def test_edge_case_single_edge(self):
        n = 2
        k = 1
        edges = [
            (0, 1, 100, 10)
        ]
        # With one patrol, the only edge can be patrolled fully.
        result = optimal_patrol_placement(n, k, edges)
        self.assertEqual(result, 0)

if __name__ == "__main__":
    unittest.main()