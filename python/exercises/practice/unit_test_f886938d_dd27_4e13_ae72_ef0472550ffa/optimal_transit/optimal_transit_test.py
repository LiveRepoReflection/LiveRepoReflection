import unittest
from optimal_transit import find_optimal_route

class OptimalTransitTest(unittest.TestCase):
    def test_direct_edge(self):
        # Simple graph with a direct edge that meets capacity requirements.
        G = [(0, 1, 10, 50)]
        start_node = 0
        end_node = 1
        num_passengers = 30  # 30/50 = 0.6 utilization
        result = find_optimal_route(G, start_node, end_node, num_passengers)
        self.assertEqual(result, [0, 1])

    def test_no_route(self):
        # Graph where the destination is unreachable.
        G = [(0, 1, 10, 50)]
        start_node = 0
        end_node = 2
        num_passengers = 20
        result = find_optimal_route(G, start_node, end_node, num_passengers)
        self.assertEqual(result, [])

    def test_capacity_failure(self):
        # Graph with a route that fails due to insufficient capacity on one edge.
        G = [(0, 1, 5, 25), (1, 2, 5, 20)]
        start_node = 0
        end_node = 2
        num_passengers = 25  # Edge (1,2) cannot handle 25 passengers since capacity is 20.
        result = find_optimal_route(G, start_node, end_node, num_passengers)
        self.assertEqual(result, [])

    def test_optimal_route_selection(self):
        # Graph taken from problem example.
        # Edges: [(0, 1, 10, 50), (0, 2, 15, 30), (1, 2, 5, 20),
        #         (1, 3, 12, 40), (2, 3, 8, 60)]
        # Expected optimal route: [0, 1, 3]
        G = [(0, 1, 10, 50), (0, 2, 15, 30), (1, 2, 5, 20), (1, 3, 12, 40), (2, 3, 8, 60)]
        start_node = 0
        end_node = 3
        num_passengers = 25
        result = find_optimal_route(G, start_node, end_node, num_passengers)
        self.assertEqual(result, [0, 1, 3])

    def test_tie_breaker_on_cost(self):
        # Two routes yield the same maximum utilization.
        # Route 1: 0->1 (10, cap=50) then 1->3 (10, cap=40) -> total cost 20.
        # Utilizations: 25/50 = 0.5 and 25/40 = 0.625.
        # Route 2: 0->2 (1, cap=50) then 2->3 (18, cap=40) -> total cost 19.
        # Expected optimal route is [0, 2, 3] due to lower total cost.
        G = [(0, 1, 10, 50), (1, 3, 10, 40), (0, 2, 1, 50), (2, 3, 18, 40)]
        start_node = 0
        end_node = 3
        num_passengers = 25
        result = find_optimal_route(G, start_node, end_node, num_passengers)
        self.assertEqual(result, [0, 2, 3])

    def test_complex_graph(self):
        # Larger graph with multiple possible paths.
        # Graph with 6 nodes and multiple potential routes.
        # Edges:
        # 0->1: cost 3, capacity 50 -> utilization 25/50 = 0.5
        # 1->4: cost 5, capacity 50 -> utilization 0.5
        # 0->2: cost 4, capacity 30 -> utilization 25/30 ≈ 0.833
        # 2->3: cost 2, capacity 40 -> utilization 25/40 = 0.625
        # 3->4: cost 1, capacity 100 -> utilization 25/100 = 0.25
        # 4->5: cost 3, capacity 40 -> utilization 25/40 = 0.625
        # 3->5: cost 5, capacity 30 -> utilization 25/30 ≈ 0.833
        # Optimal route is [0, 1, 4, 5] with maximum utilization 0.5.
        G = [
            (0, 1, 3, 50),
            (1, 4, 5, 50),
            (0, 2, 4, 30),
            (2, 3, 2, 40),
            (3, 4, 1, 100),
            (4, 5, 3, 40),
            (3, 5, 5, 30)
        ]
        start_node = 0
        end_node = 5
        num_passengers = 25
        result = find_optimal_route(G, start_node, end_node, num_passengers)
        self.assertEqual(result, [0, 1, 4, 5])

    def test_direct_cycle(self):
        # Graph containing a cycle to ensure the algorithm does not loop indefinitely.
        # Graph: 0->1, 1->0, and 1->2.
        # Expected route: [0, 1, 2].
        G = [(0, 1, 5, 50), (1, 0, 5, 50), (1, 2, 5, 50)]
        start_node = 0
        end_node = 2
        num_passengers = 25
        result = find_optimal_route(G, start_node, end_node, num_passengers)
        self.assertEqual(result, [0, 1, 2])

if __name__ == '__main__':
    unittest.main()