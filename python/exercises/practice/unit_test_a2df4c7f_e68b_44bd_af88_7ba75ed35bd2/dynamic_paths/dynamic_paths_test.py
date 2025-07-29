import unittest
from dynamic_paths import solve_dynamic_paths

class DynamicPathsTest(unittest.TestCase):
    def test_basic_updates(self):
        # Test case with a small graph and two updates (road update, then source update)
        N = 4
        roads = [(0, 1, 2), (1, 2, 3)]
        sources = [0]
        updates = [
            (0, 2, 3, 1),   # Road update: add road from city 2 to 3 with length 1
            (1, 1, True)    # Source update: add city 1 to the sources
        ]
        # After first update:
        # Distances from sources = [0]: 0->0: 0, 0->1: 2, 0->2: 5, 0->3: 6  => sum = 0+2+5+6 = 13
        # After second update: sources = [0, 1]:
        # For each city:
        # City 0: min(0, inf) = 0
        # City 1: min(2, 0) = 0
        # City 2: min(5, 3) = 3   (from source 1 via 1->2)
        # City 3: min(6, 4) = 4   (from source 1: 1->2->3: 3+1=4)
        # Sum = 0+0+3+4 = 7
        expected = [13, 7]
        result = solve_dynamic_paths(N, roads, sources, updates)
        self.assertEqual(result, expected)

    def test_single_city_source_update(self):
        # Minimal case with one city and initially no sources.
        N = 1
        roads = []
        sources = []
        updates = [
            (1, 0, True)   # Source update: add city 0
        ]
        # Only one city, from source city 0 the distance is 0, sum = 0.
        expected = [0]
        result = solve_dynamic_paths(N, roads, sources, updates)
        self.assertEqual(result, expected)

    def test_unreachable_and_source_removal(self):
        # Graph with unreachable nodes.
        N = 3
        roads = [(0, 1, 5)]
        sources = [0]
        updates = [
            (0, 1, 2, 3),   # Road update: add road from city 1 to 2 with length 3.
            (1, 0, False)   # Source update: remove city 0.
        ]
        # After first update: distances from source [0]:
        # City 0: 0
        # City 1: 5
        # City 2: 5+3 = 8
        # Sum = 0+5+8 = 13
        # After second update: now no source available,
        # all nodes are unreachable, so each distance is -1, sum = -1 * 3 = -3.
        expected = [13, -3]
        result = solve_dynamic_paths(N, roads, sources, updates)
        self.assertEqual(result, expected)

    def test_complex_multiple_updates(self):
        # Larger graph with multiple updates and source changes.
        N = 5
        roads = [(0, 1, 10), (1, 2, 10), (2, 3, 10), (3, 4, 10)]
        sources = [0]
        updates = [
            (0, 3, 2, 5),   # Road update: add edge from city 3 to 2 with weight 5.
            (1, 3, True),   # Source update: add city 3 to the sources.
            (0, 4, 2, 2)    # Road update: add edge from city 4 to 2 with weight 2.
        ]
        # After update1: from source [0]:
        # City0: 0
        # City1: 10
        # City2: 20    (via 0->1->2)
        # City3: 30
        # City4: 40
        # (New edge (3->2) does not affect shortest paths from source 0)
        # Sum = 0 + 10 + 20 + 30 + 40 = 100
        #
        # After update2: sources = [0, 3]:
        # Distances:
        # City0: 0
        # City1: 10          (reachable only from 0)
        # City2: min(20 from 0, 5 from 3 via 3->2) = 5
        # City3: min(30 from 0, 0 from 3) = 0
        # City4: min(40 from 0, 10 from 3 via 3->4) = 10
        # Sum = 0 + 10 + 5 + 0 + 10 = 25
        #
        # After update3: new edge (4->2) with weight 2.
        # This does not change the optimum distances:
        # City2: remains min(20 from 0, 5 from 3, 3->4->2 route would be 10+2=12) = 5
        # Sum = still 25.
        expected = [100, 25, 25]
        result = solve_dynamic_paths(N, roads, sources, updates)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()