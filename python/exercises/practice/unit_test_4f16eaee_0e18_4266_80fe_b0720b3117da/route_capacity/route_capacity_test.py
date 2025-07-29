import unittest
from route_capacity import optimal_route


class RouteCapacityTest(unittest.TestCase):
    def test_basic_example(self):
        N = 4
        edges = [(0, 1, 10, 5), (0, 2, 15, 3), (1, 3, 12, 4), (2, 3, 10, 6)]
        capacities = [10, 5, 8, 10]
        S = 0
        D = 3
        expected = [0, 1, 3]
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_no_route_available(self):
        N = 3
        edges = [(0, 1, 5, 2), (1, 2, 5, 0)]  # Zero bandwidth on edge 1->2
        capacities = [10, 5, 10]
        S = 0
        D = 2
        expected = []
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_zero_node_capacity(self):
        N = 4
        edges = [(0, 1, 5, 5), (1, 2, 5, 5), (2, 3, 5, 5)]
        capacities = [10, 0, 10, 10]  # Zero capacity at node 1
        S = 0
        D = 3
        expected = []
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_multiple_possible_routes(self):
        N = 5
        edges = [
            (0, 1, 10, 5), (0, 2, 10, 5),  # Two equal paths from 0
            (1, 3, 10, 5), (2, 3, 10, 5),  # Two equal paths to 3
            (3, 4, 10, 5)
        ]
        capacities = [10, 5, 5, 5, 10]
        S = 0
        D = 4
        # Either [0, 1, 3, 4] or [0, 2, 3, 4] is valid, so we check the length and endpoints
        result = optimal_route(N, edges, capacities, S, D)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[-1], 4)

    def test_direct_route_vs_shorter_multihop(self):
        N = 3
        edges = [(0, 1, 5, 5), (1, 2, 5, 5), (0, 2, 15, 5)]  # Direct route has higher latency
        capacities = [10, 5, 10]
        S = 0
        D = 2
        expected = [0, 1, 2]  # Should choose route with lower total latency
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_multiple_edges_between_nodes(self):
        N = 3
        edges = [(0, 1, 10, 5), (0, 1, 5, 2), (1, 2, 5, 5)]  # Multiple edges between 0 and 1
        capacities = [10, 5, 10]
        S = 0
        D = 2
        expected = [0, 1, 2]  # Should choose the edge with lower latency
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_unreachable_destination(self):
        N = 4
        edges = [(0, 1, 5, 5), (2, 3, 5, 5)]  # No path from 0 to 3
        capacities = [10, 5, 10, 10]
        S = 0
        D = 3
        expected = []
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_complex_graph(self):
        N = 6
        edges = [
            (0, 1, 5, 5), (0, 2, 3, 5), (1, 3, 6, 5), (1, 4, 8, 5),
            (2, 3, 4, 5), (2, 4, 7, 5), (3, 5, 9, 5), (4, 5, 2, 5)
        ]
        capacities = [10, 5, 5, 5, 5, 10]
        S = 0
        D = 5
        expected = [0, 2, 4, 5]  # Route with minimum latency
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_large_graph(self):
        # Creating a linear graph with 100 nodes
        N = 100
        edges = []
        for i in range(N-1):
            edges.append((i, i+1, 1, 5))
        capacities = [5] * N
        S = 0
        D = N-1
        expected = list(range(N))  # Only one path possible
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_graph_with_cycles(self):
        N = 5
        edges = [
            (0, 1, 5, 5), (1, 2, 5, 5), (2, 3, 5, 5), (3, 4, 5, 5),
            (0, 3, 15, 5), (1, 4, 15, 5)  # Creating cycles
        ]
        capacities = [10, 5, 5, 5, 10]
        S = 0
        D = 4
        expected = [0, 1, 2, 3, 4]  # Shortest path despite cycles
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_self_loops(self):
        N = 4
        edges = [(0, 0, 5, 5), (0, 1, 5, 5), (1, 2, 5, 5), (2, 3, 5, 5)]  # Self-loop at node 0
        capacities = [10, 5, 5, 10]
        S = 0
        D = 3
        expected = [0, 1, 2, 3]  # Should ignore self-loop
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_bidirectional_edges(self):
        N = 4
        edges = [
            (0, 1, 5, 5), (1, 0, 5, 5),  # Bidirectional between 0 and 1
            (1, 2, 5, 5), (2, 1, 5, 5),  # Bidirectional between 1 and 2
            (2, 3, 5, 5), (3, 2, 5, 5)   # Bidirectional between 2 and 3
        ]
        capacities = [10, 5, 5, 10]
        S = 0
        D = 3
        expected = [0, 1, 2, 3]
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)

    def test_direct_route_limited_bandwidth(self):
        N = 3
        edges = [(0, 2, 10, 0), (0, 1, 5, 5), (1, 2, 5, 5)]  # Direct route has zero bandwidth
        capacities = [10, 5, 10]
        S = 0
        D = 2
        expected = [0, 1, 2]  # Should choose route with sufficient bandwidth
        self.assertEqual(optimal_route(N, edges, capacities, S, D), expected)


if __name__ == '__main__':
    unittest.main()