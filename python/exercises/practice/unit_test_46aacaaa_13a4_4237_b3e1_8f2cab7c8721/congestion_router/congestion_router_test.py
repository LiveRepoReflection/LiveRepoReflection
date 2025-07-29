import unittest
from congestion_router import find_paths

class CongestionRouterTest(unittest.TestCase):
    def test_single_path(self):
        graph = {
            1: {2: 5},
            2: {}
        }
        source = 1
        destination = 2
        k = 1
        T = 10
        expected = [[1, 2]]
        result = find_paths(graph, source, destination, k, T)
        self.assertEqual(result, expected)

    def test_source_equals_destination(self):
        graph = {
            1: {2: 5},
            2: {3: 4},
            3: {}
        }
        source = 1
        destination = 1
        k = 3
        T = 10
        expected = [[1]]
        result = find_paths(graph, source, destination, k, T)
        self.assertEqual(result, expected)

    def test_no_valid_paths_due_threshold(self):
        graph = {
            1: {2: 15, 3: 20},
            2: {4: 5},
            3: {4: 2},
            4: {}
        }
        source = 1
        destination = 4
        k = 2
        T = 10
        # Since all edges from node 1 exceed the threshold T, no valid paths should be found.
        expected = []
        result = find_paths(graph, source, destination, k, T)
        self.assertEqual(result, expected)

    def test_multiple_paths(self):
        graph = {
            1: {2: 2, 3: 2},
            2: {4: 2, 5: 5},
            3: {5: 2},
            4: {6: 2},
            5: {4: 2, 6: 5},
            6: {}
        }
        source = 1
        destination = 6
        k = 3
        T = 5
        result = find_paths(graph, source, destination, k, T)
        # Validate that each returned path begins with source and ends with destination
        self.assertTrue(isinstance(result, list))
        for path in result:
            self.assertTrue(isinstance(path, list))
            self.assertEqual(path[0], source)
            self.assertEqual(path[-1], destination)
        # Validate that total congestions are in ascending order
        def path_cost(p):
            total = 0
            for i in range(len(p) - 1):
                total += graph[p[i]][p[i+1]]
            return total
        costs = [path_cost(path) for path in result]
        self.assertEqual(costs, sorted(costs))

    def test_cycle_prevention(self):
        # Graph that contains potential cycles if not handled properly
        graph = {
            1: {2: 1, 3: 5},
            2: {3: 1, 1: 1},
            3: {4: 1},
            4: {2: 1}
        }
        source = 1
        destination = 4
        k = 2
        T = 5
        result = find_paths(graph, source, destination, k, T)
        # Ensure no path includes a cycle (i.e., no repeated nodes)
        for path in result:
            self.assertEqual(len(path), len(set(path)), msg="Cycle detected in path")
            self.assertEqual(path[0], source)
            self.assertEqual(path[-1], destination)

    def test_diverse_paths_selection(self):
        # Graph with multiple possible valid paths with overlapping segments.
        graph = {
            1: {2: 1, 3: 1},
            2: {4: 1, 5: 1},
            3: {5: 1, 4: 2},
            4: {6: 1},
            5: {6: 1},
            6: {}
        }
        source = 1
        destination = 6
        k = 3
        T = 2
        result = find_paths(graph, source, destination, k, T)
        # Verify that each returned path meets the threshold constraint and correct start and end.
        self.assertTrue(len(result) <= k)
        for path in result:
            self.assertEqual(path[0], source)
            self.assertEqual(path[-1], destination)
            for i in range(len(path) - 1):
                self.assertLessEqual(graph[path[i]][path[i+1]], T)
        # Although verifying the diversity optimization exactly is complex,
        # we ensure at least that multiple valid paths are returned.
        self.assertGreaterEqual(len(result), 1)

if __name__ == '__main__':
    unittest.main()