import unittest
from route_advisor import plan_route

class TestRouteAdvisor(unittest.TestCase):

    def setUp(self):
        # Sample graph represented as a list of edges:
        # Each edge is a tuple: (start_intersection_id, destination_intersection_id, travel_time, traffic_density_factor, toll_cost)
        self.graph = [
            (1, 2, 10, 0.5, 2),  # Effective travel time = 10 * 0.5 = 5, toll = 2
            (2, 3, 15, 1.0, 3),  # Effective travel time = 15 * 1.0 = 15, toll = 3
            (1, 3, 30, 0.7, 4),  # Effective travel time = 30 * 0.7 = 21, toll = 4
            (2, 4, 5, 1.0, 1),   # Effective travel time = 5 * 1.0 = 5, toll = 1
            (4, 3, 5, 1.0, 1)    # Effective travel time = 5 * 1.0 = 5, toll = 1
        ]

    def test_simple_optimal_route(self):
        # Test the optimal route from 1 to 3.
        # Two possible routes:
        # 1->3: effective time = 21, toll = 4
        # 1->2->4->3: effective time = 5 (1->2) + 5 (2->4) + 5 (4->3) = 15, toll = 2+1+1 = 4
        request = {
            'start': 1,
            'end': 3,
            'departure_time': 0,
            'max_budget': 5
        }
        route, total_time, total_toll = plan_route(self.graph, request)
        expected_route = [1, 2, 4, 3]
        self.assertEqual(route, expected_route)
        self.assertAlmostEqual(total_time, 15)
        self.assertAlmostEqual(total_toll, 4)

    def test_insufficient_budget(self):
        # With a max_budget below the toll requirements, no route should be found.
        request = {
            'start': 1,
            'end': 3,
            'departure_time': 0,
            'max_budget': 3  # Both possible routes require toll of 4.
        }
        route, total_time, total_toll = plan_route(self.graph, request)
        self.assertEqual(route, [])
        self.assertEqual(total_time, 0)
        self.assertEqual(total_toll, 0)

    def test_same_start_and_end(self):
        # When start and destination are the same, the optimal path is trivial.
        request = {
            'start': 1,
            'end': 1,
            'departure_time': 10,
            'max_budget': 10
        }
        route, total_time, total_toll = plan_route(self.graph, request)
        self.assertEqual(route, [1])
        self.assertEqual(total_time, 0)
        self.assertEqual(total_toll, 0)

    def test_no_route_possible(self):
        # Create a graph where the destination is unreachable.
        graph_unreachable = [
            (1, 2, 10, 0.5, 2)
            # Node 3 is completely disconnected.
        ]
        request = {
            'start': 1,
            'end': 3,
            'departure_time': 0,
            'max_budget': 10
        }
        route, total_time, total_toll = plan_route(graph_unreachable, request)
        self.assertEqual(route, [])
        self.assertEqual(total_time, 0)
        self.assertEqual(total_toll, 0)

    def test_budget_edge_case_exact_budget(self):
        # Test when the maximum toll budget exactly meets the route's toll cost.
        # For route 1->2->4->3, the toll is exactly 4.
        request = {
            'start': 1,
            'end': 3,
            'departure_time': 0,
            'max_budget': 4
        }
        route, total_time, total_toll = plan_route(self.graph, request)
        expected_route = [1, 2, 4, 3]
        self.assertEqual(route, expected_route)
        self.assertAlmostEqual(total_time, 15)
        self.assertAlmostEqual(total_toll, 4)

    def test_invalid_input_negative_travel_time(self):
        # Construct a graph with a negative travel time which should be invalid.
        invalid_graph = [
            (1, 2, -10, 0.5, 2),
            (2, 3, 15, 1.0, 3)
        ]
        request = {
            'start': 1,
            'end': 3,
            'departure_time': 0,
            'max_budget': 10
        }
        with self.assertRaises(ValueError):
            plan_route(invalid_graph, request)

    def test_invalid_input_invalid_intersections(self):
        # Request with non-existent intersection.
        request = {
            'start': 10,
            'end': 20,
            'departure_time': 0,
            'max_budget': 10
        }
        route, total_time, total_toll = plan_route(self.graph, request)
        # When intersections are invalid, the function should return no route.
        self.assertEqual(route, [])
        self.assertEqual(total_time, 0)
        self.assertEqual(total_toll, 0)

if __name__ == '__main__':
    unittest.main()