import unittest
from intergalactic_path import find_shortest_path

class IntergalacticPathTest(unittest.TestCase):
    def test_direct_route(self):
        # Simple direct route with a single wormhole that maintains resource constraints.
        n = 2
        adj = [
            [(1, 5, [(0, 1)])],  # Station 0 to station 1, degrades resource 0 by 1.
            []
        ]
        start = 0
        end = 1
        resources = [10]
        resource_thresholds = [5]
        # After the journey, resource[0] becomes 9 which is >= the threshold of 5.
        self.assertEqual(find_shortest_path(n, adj, start, end, resources, resource_thresholds), 5)

    def test_example_case(self):
        # Provided example:
        n = 3
        adj = [
            [(1, 5, [(0, 10)]), (2, 10, [(1, 5)])],
            [(2, 3, [(0, 5), (1, 2)])],
            []
        ]
        start = 0
        end = 2
        resources = [50, 30]
        resource_thresholds = [15, 10]
        # Expected path: 0 -> 1 -> 2 with total distance 5 + 3 = 8.
        self.assertEqual(find_shortest_path(n, adj, start, end, resources, resource_thresholds), 8)

    def test_insufficient_resources(self):
        # Test case where the resource depletion causes the journey to be invalid.
        n = 2
        adj = [
            [(1, 5, [(0, 10)])],
            []
        ]
        start = 0
        end = 1
        resources = [10]   # Depletion leads to 0 which is below the threshold.
        resource_thresholds = [1]
        self.assertEqual(find_shortest_path(n, adj, start, end, resources, resource_thresholds), -1)

    def test_cycle(self):
        # Graph contains a cycle that must be handled properly.
        n = 4
        adj = [
            [(1, 2, [(0, 1)])],                 # 0 -> 1
            [(2, 2, [(0, 1)])],                 # 1 -> 2
            [(0, 2, [(0, 1)]), (3, 5, [(0, 2)])],# 2 -> 0 (cycle) and 2 -> 3 (valid route)
            []
        ]
        start = 0
        end = 3
        resources = [10]
        resource_thresholds = [5]
        # Valid path: 0 -> 1 -> 2 -> 3 with distance 2 + 2 + 5 = 9.
        self.assertEqual(find_shortest_path(n, adj, start, end, resources, resource_thresholds), 9)

    def test_multiple_paths(self):
        # Two potential paths where one is invalid due to excessive degradation.
        n = 3
        adj = [
            [(1, 3, [(0, 8)]), (2, 10, [(0, 2)])],
            [(2, 3, [(0, 0)])],
            []
        ]
        start = 0
        end = 2
        resources = [10]
        resource_thresholds = [3]
        # Path 0->1->2 would reduce resource[0] to 2 (< threshold of 3), so only the direct 0->2 path is valid.
        self.assertEqual(find_shortest_path(n, adj, start, end, resources, resource_thresholds), 10)

    def test_unreachable(self):
        # Test case where there is no path between start and end.
        n = 3
        adj = [
            [(1, 4, [(0, 1)])],
            [],
            []
        ]
        start = 0
        end = 2
        resources = [100]
        resource_thresholds = [10]
        self.assertEqual(find_shortest_path(n, adj, start, end, resources, resource_thresholds), -1)

if __name__ == '__main__':
    unittest.main()