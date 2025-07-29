import unittest
from hyper_interconnect import route_data

class TestHyperInterconnect(unittest.TestCase):

    def test_basic_connections(self):
        N = 5
        hyperedges = [[0, 1, 2], [2, 3, 4]]
        requests = [(0, 4), (1, 3), (0, 0)]
        expected = [2, 2, 0]
        result = route_data(N, hyperedges, requests)
        self.assertEqual(result, expected)

    def test_unreachable(self):
        N = 4
        hyperedges = [[0, 1], [2, 3]]
        requests = [(0, 3), (1, 2)]
        expected = [-1, -1]
        result = route_data(N, hyperedges, requests)
        self.assertEqual(result, expected)

    def test_direct_connection(self):
        N = 6
        hyperedges = [[0, 1, 2, 3], [3, 4, 5]]
        requests = [(0, 2), (3, 5)]
        # In hyperedges [0,1,2,3] and [3,4,5], 0->2 is in the same hyperedge (1 traversal)
        # 3->5 is in the same hyperedge [3,4,5] (1 traversal)
        expected = [1, 1]
        result = route_data(N, hyperedges, requests)
        self.assertEqual(result, expected)

    def test_duplicate_servers_in_hyperedges(self):
        N = 5
        hyperedges = [[0, 1, 1, 2], [2, 3, 3, 4]]
        requests = [(0, 4), (1, 3)]
        expected = [2, 2]
        result = route_data(N, hyperedges, requests)
        self.assertEqual(result, expected)

    def test_multiple_paths(self):
        # Multiple hyperedges can lead to the destination; ensure the minimum number is found.
        N = 7
        hyperedges = [
            [0, 1, 2],
            [2, 3],
            [1, 4],
            [4, 5],
            [3, 6],
            [5, 6]
        ]
        requests = [(0, 6), (4, 6)]
        # For request (0,6):
        # Option 1: 0->2 (edge1) -> 3 (edge2) -> 6 (edge5): 3 traversals.
        # Option 2: 0->1 (edge1) -> 4 (edge3) -> 5 (edge4) -> 6 (edge6): 4 traversals.
        # Minimum is 3.
        # For request (4,6):
        # Option 1: 4->5 (edge4) -> 6 (edge6): 2 traversals.
        expected = [3, 2]
        result = route_data(N, hyperedges, requests)
        self.assertEqual(result, expected)

    def test_large_single_hyperedge(self):
        # When all servers are in one hyperedge, any two distinct servers use one traversal.
        N = 100
        hyperedges = [list(range(100))]
        requests = [(10, 90), (0, 99), (50, 50)]
        expected = [1, 1, 0]
        result = route_data(N, hyperedges, requests)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()