import unittest
from network_routes import find_optimal_routes


class NetworkRoutesTest(unittest.TestCase):
    def test_single_path(self):
        n = 3
        edges = [(0, 1, 10, 5), (1, 2, 15, 8)]
        start = 0
        end = 2
        k = 1
        expected = [[0, 1, 2]]
        self.assertCountEqual(find_optimal_routes(n, edges, start, end, k), expected)

    def test_multiple_paths(self):
        n = 4
        edges = [
            (0, 1, 10, 5),
            (1, 3, 15, 10),
            (0, 2, 8, 3),
            (2, 3, 12, 6)
        ]
        start = 0
        end = 3
        k = 2
        # Path 0-1-3: bandwidth=min(10,15)=10, cost=5+10=15, utility=10/15=0.667
        # Path 0-2-3: bandwidth=min(8,12)=8, cost=3+6=9, utility=8/9=0.889
        # Path 0-2-3 has higher utility
        expected = [[0, 2, 3], [0, 1, 3]]
        result = find_optimal_routes(n, edges, start, end, k)
        
        # Check if the correct paths are returned (order might vary)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(path in expected for path in result))
        
        # Check the first path has higher utility than the second
        utilities = []
        for path in result:
            if path == [0, 1, 3]:
                utilities.append(10/15)
            elif path == [0, 2, 3]:
                utilities.append(8/9)
        self.assertTrue(utilities[0] >= utilities[1])

    def test_start_equals_end(self):
        n = 3
        edges = [(0, 1, 10, 5), (1, 2, 15, 8)]
        start = 1
        end = 1
        k = 1
        expected = [[1]]
        self.assertEqual(find_optimal_routes(n, edges, start, end, k), expected)

    def test_disconnected_graph(self):
        n = 5
        edges = [(0, 1, 10, 5), (2, 3, 15, 8), (3, 4, 20, 10)]
        start = 0
        end = 4
        k = 1
        expected = []
        self.assertEqual(find_optimal_routes(n, edges, start, end, k), expected)

    def test_zero_bandwidth(self):
        n = 3
        edges = [(0, 1, 0, 5), (1, 2, 15, 8)]
        start = 0
        end = 2
        k = 1
        expected = []
        self.assertEqual(find_optimal_routes(n, edges, start, end, k), expected)

    def test_zero_cost(self):
        n = 3
        edges = [(0, 1, 10, 0), (1, 2, 15, 8)]
        start = 0
        end = 2
        k = 1
        expected = []
        self.assertEqual(find_optimal_routes(n, edges, start, end, k), expected)

    def test_k_greater_than_possible_paths(self):
        n = 4
        edges = [
            (0, 1, 10, 5),
            (1, 3, 15, 10),
            (0, 2, 8, 3),
            (2, 3, 12, 6)
        ]
        start = 0
        end = 3
        k = 5  # There are only 2 possible paths
        result = find_optimal_routes(n, edges, start, end, k)
        self.assertEqual(len(result), 2)

    def test_large_network(self):
        # Create a larger network with multiple paths
        n = 8
        edges = [
            (0, 1, 10, 5), (0, 2, 8, 3), (0, 3, 6, 2),
            (1, 4, 12, 7), (2, 4, 9, 4), (3, 5, 7, 3),
            (4, 6, 15, 9), (5, 6, 11, 6), (5, 7, 13, 8),
            (6, 7, 14, 10)
        ]
        start = 0
        end = 7
        k = 3
        result = find_optimal_routes(n, edges, start, end, k)
        
        # Check there are up to 3 paths
        self.assertTrue(1 <= len(result) <= 3)
        
        # Check all paths start with 0 and end with 7
        for path in result:
            self.assertEqual(path[0], 0)
            self.assertEqual(path[-1], 7)

    def test_paths_with_same_utility(self):
        n = 4
        edges = [
            (0, 1, 10, 5), (1, 3, 10, 5),  # Path 0-1-3 with utility 10/10 = 1
            (0, 2, 8, 4), (2, 3, 8, 4)     # Path 0-2-3 with utility 8/8 = 1
        ]
        start = 0
        end = 3
        k = 2
        result = find_optimal_routes(n, edges, start, end, k)
        
        # Both paths have the same utility, so ordering doesn't matter
        self.assertEqual(len(result), 2)
        path_options = [[0, 1, 3], [0, 2, 3]]
        for path in result:
            self.assertTrue(path in path_options)
        
    def test_complex_network(self):
        n = 10
        edges = [
            (0, 1, 20, 10), (0, 2, 15, 5), (0, 3, 10, 3),
            (1, 4, 18, 9), (1, 5, 16, 8), (2, 5, 14, 7),
            (2, 6, 12, 6), (3, 6, 8, 4), (3, 7, 6, 3),
            (4, 8, 17, 8), (5, 8, 15, 7), (6, 8, 13, 6),
            (6, 9, 11, 5), (7, 9, 7, 3), (8, 9, 19, 10)
        ]
        start = 0
        end = 9
        k = 3
        result = find_optimal_routes(n, edges, start, end, k)
        
        # Check there are up to 3 paths
        self.assertTrue(1 <= len(result) <= 3)
        
        # Check all paths start with 0 and end with 9
        for path in result:
            self.assertEqual(path[0], 0)
            self.assertEqual(path[-1], 9)