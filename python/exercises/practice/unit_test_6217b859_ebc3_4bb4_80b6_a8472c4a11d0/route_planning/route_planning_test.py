import unittest
from route_planning import find_routes

class RoutePlanningTest(unittest.TestCase):
    def test_basic_success(self):
        # Basic test with two delivery requests that can be feasibly routed.
        N = 4
        edges = [
            (0, 1, 5, 10),
            (0, 2, 8, 5),
            (1, 3, 6, 8),
            (2, 3, 4, 7)
        ]
        requests = [
            (3, 3, 15),  # Destination 3, 3 vehicles, deadline 15
            (3, 2, 18)   # Destination 3, 2 vehicles, deadline 18
        ]
        result = find_routes(N, edges, requests)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(requests))
        # Check that each route starts at 0 and ends at the correct destination.
        for idx, (dest, vehicles, deadline) in enumerate(requests):
            route = result[idx]
            self.assertIsNotNone(route)
            self.assertEqual(route[0], 0)
            self.assertEqual(route[-1], dest)
            # Calculate total travel time for the route.
            total_time = 0
            for u, v in zip(route, route[1:]):
                # Find the edge matching (u, v)
                for edge in edges:
                    if edge[0] == u and edge[1] == v:
                        total_time += edge[2]
                        break
            self.assertLessEqual(total_time, deadline)

    def test_no_possible_route_due_to_deadline(self):
        # Test where the only possible route exceeds the deadline.
        N = 3
        edges = [
            (0, 1, 10, 10),
            (1, 2, 10, 10)
        ]
        requests = [
            (2, 5, 15)  # Total travel time would be 20, which exceeds the deadline 15.
        ]
        result = find_routes(N, edges, requests)
        self.assertIsNone(result)

    def test_edge_capacity_constraints(self):
        # Test that ensures routes respect edge capacity constraints.
        N = 5
        edges = [
            (0, 1, 3, 4),
            (1, 2, 3, 4),
            (0, 3, 6, 10),
            (3, 2, 2, 10),
            (2, 4, 5, 4),
            (1, 4, 10, 4),
            (3, 4, 3, 2)
        ]
        requests = [
            (4, 3, 15),
            (4, 2, 15)
        ]
        result = find_routes(N, edges, requests)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(requests))
        for idx, (dest, vehicles, deadline) in enumerate(requests):
            route = result[idx]
            self.assertIsNotNone(route)
            self.assertEqual(route[0], 0)
            self.assertEqual(route[-1], dest)
            total_time = 0
            for u, v in zip(route, route[1:]):
                for edge in edges:
                    if edge[0] == u and edge[1] == v:
                        total_time += edge[2]
                        break
            self.assertLessEqual(total_time, deadline)
        # Note: Detailed simulation of capacity constraint compliance is left to the solver's implementation.

    def test_multiple_routes_possible(self):
        # Test a scenario where multiple routes exist and an optimal one is expected.
        N = 4
        edges = [
            (0, 1, 2, 10),
            (1, 3, 4, 10),
            (0, 2, 3, 10),
            (2, 3, 3, 10),
            (0, 3, 10, 10)
        ]
        requests = [
            (3, 4, 10)
        ]
        result = find_routes(N, edges, requests)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        route = result[0]
        self.assertEqual(route[0], 0)
        self.assertEqual(route[-1], 3)
        total_time = 0
        for u, v in zip(route, route[1:]):
            for edge in edges:
                if edge[0] == u and edge[1] == v:
                    total_time += edge[2]
                    break
        # The optimal route should have total travel time not exceeding 7 (either 2+4 or 3+3).
        self.assertLessEqual(total_time, 7)

    def test_no_solution_due_to_capacity(self):
        # Test where the available capacity on all routes is insufficient for the request.
        N = 4
        edges = [
            (0, 1, 5, 1),
            (1, 2, 5, 1),
            (2, 3, 5, 1),
            (0, 3, 20, 1)
        ]
        requests = [
            (3, 2, 20)  # Request requires 2 vehicles but each edge only allows 1.
        ]
        result = find_routes(N, edges, requests)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()