import unittest
from service_routing import min_total_cost

class ServiceRoutingTest(unittest.TestCase):
    def test_direct_vs_indirect(self):
        # Three services with ample capacity.
        N = 3
        capacities = [100, 100, 100]
        graph = [(0, 1, 10), (1, 2, 10), (0, 2, 25)]
        M = 1
        messages = [(0, 2, 10)]
        # Expected: using route 0->1->2: cost = 10 + 10 = 20.
        expected_cost = 20
        self.assertEqual(min_total_cost(N, capacities, graph, M, messages), expected_cost)

    def test_capacity_depletion(self):
        # Test where capacity constraints cause an impossible message delivery.
        N = 3
        capacities = [20, 20, 20]
        graph = [(0, 1, 10), (1, 2, 10), (0, 2, 25)]
        M = 2
        messages = [(0, 1, 10), (0, 2, 15)]
        # After the first message, service 0 and 1 capacities drop to 10.
        # The second message cannot be sent because service 0 (or intermediaries) have insufficient capacity.
        expected_cost = -1
        self.assertEqual(min_total_cost(N, capacities, graph, M, messages), expected_cost)

    def test_multiple_messages_with_alternate_paths(self):
        # Four services connected in a cycle with additional edges.
        N = 4
        capacities = [50, 50, 50, 50]
        graph = [
            (0, 1, 5), (1, 2, 5), (2, 3, 5), (0, 3, 20),
            (1, 3, 10), (0, 2, 15), (2, 0, 15)
        ]
        M = 2
        messages = [
            (0, 3, 10),  # Optimal route: 0->1->2->3 with cost 5+5+5 = 15.
            (3, 0, 10)   # No available route from 3 back to 0.
        ]
        expected_cost = -1
        self.assertEqual(min_total_cost(N, capacities, graph, M, messages), expected_cost)

    def test_multiple_routes_prefer_less_hops(self):
        # Test that when routes have equal cost, the path with fewer hops is chosen.
        N = 3
        capacities = [100, 100, 100]
        graph = [(0, 1, 10), (1, 2, 10), (0, 2, 20)]
        M = 1
        messages = [(0, 2, 5)]
        # Both 0->1->2 and 0->2 yield a cost of 20, but the direct path is preferred.
        expected_cost = 20
        self.assertEqual(min_total_cost(N, capacities, graph, M, messages), expected_cost)

    def test_route_with_exact_capacity(self):
        # Test where service capacities exactly suffice for message delivery.
        N = 3
        capacities = [10, 10, 10]
        graph = [(0, 1, 7), (1, 2, 8), (0, 2, 20)]
        M = 1
        messages = [(0, 2, 10)]
        # Direct route (0,2) uses only services 0 and 2 and costs 20.
        # Indirect route (0->1->2) costs 7+8 = 15 and uses all three services.
        # Expected optimal cost is 15.
        expected_cost = 15
        self.assertEqual(min_total_cost(N, capacities, graph, M, messages), expected_cost)

if __name__ == "__main__":
    unittest.main()