import unittest
from intermodal_route import route_planner

class TestIntermodalRoute(unittest.TestCase):
    def test_direct_connection(self):
        cities = ["A", "B"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 10, 20)
        ]
        start_city = "A"
        end_city = "B"
        budget = 50
        time_limit = 30
        mode_restrictions = {}
        expected = [("A", "B", "train", 10, 20)]
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, mode_restrictions)
        self.assertEqual(result, expected)

    def test_multiple_routes_choose_shortest_time(self):
        cities = ["A", "B", "C", "D"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 5, 15),
            ("B", "D", "truck", 5, 10),
            ("A", "C", "truck", 8, 12),
            ("C", "D", "airplane", 7, 8),
            ("A", "D", "ship", 20, 30)
        ]
        start_city = "A"
        end_city = "D"
        budget = 20
        time_limit = 40
        # Possible routes:
        # A -> B -> D: time = 15 + 10 = 25, cost = 5 + 5 = 10
        # A -> C -> D: time = 12 + 8 = 20, cost = 8 + 7 = 15
        # A -> D: time = 30, cost = 20 (not optimal in time)
        # Expected optimal route: A -> C -> D (minimal total time)
        expected = [("A", "C", "truck", 8, 12), ("C", "D", "airplane", 7, 8)]
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, {})
        self.assertEqual(result, expected)

    def test_tie_breaker_lower_cost(self):
        cities = ["A", "B", "C", "D"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 5, 10),
            ("B", "D", "truck", 10, 10),
            ("A", "C", "truck", 10, 10),
            ("C", "D", "airplane", 5, 10)
        ]
        start_city = "A"
        end_city = "D"
        budget = 20
        time_limit = 25
        # Both routes A->B->D and A->C->D have total time 20 and total cost 15.
        # Either valid optimal answer can be accepted.
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, {})
        valid_options = [
            [("A", "B", "train", 5, 10), ("B", "D", "truck", 10, 10)],
            [("A", "C", "truck", 10, 10), ("C", "D", "airplane", 5, 10)]
        ]
        self.assertIn(result, valid_options)

    def test_mode_restrictions(self):
        cities = ["A", "B", "C", "D"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 5, 10),
            ("B", "C", "truck", 7, 15),
            ("C", "D", "airplane", 6, 10),
            ("B", "D", "ship", 12, 5)
        ]
        start_city = "A"
        end_city = "D"
        budget = 30
        time_limit = 35
        mode_restrictions = {"B": {"train", "truck"}}
        # Route A->B->D using "ship" is not allowed due to mode restriction at B.
        expected = [("A", "B", "train", 5, 10), ("B", "C", "truck", 7, 15), ("C", "D", "airplane", 6, 10)]
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, mode_restrictions)
        self.assertEqual(result, expected)

    def test_budget_constraint(self):
        cities = ["A", "B", "C"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 15, 10),
            ("B", "C", "truck", 15, 10),
            ("A", "C", "airplane", 40, 15)
        ]
        start_city = "A"
        end_city = "C"
        budget = 25
        time_limit = 30
        # Only possible route A->B->C exceeds budget (15+15=30). Hence, no valid route.
        expected = []
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, {})
        self.assertEqual(result, expected)

    def test_time_limit_constraint(self):
        cities = ["A", "B", "C"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 5, 20),
            ("B", "C", "truck", 5, 20),
            ("A", "C", "airplane", 15, 45)
        ]
        start_city = "A"
        end_city = "C"
        budget = 50
        time_limit = 30
        # Both routes exceed the time limit.
        expected = []
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, {})
        self.assertEqual(result, expected)

    def test_cycle_route_possible(self):
        cities = ["A", "B", "C", "D"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 5, 10),
            ("B", "C", "truck", 5, 10),
            ("C", "B", "truck", 5, 10),  # cycle between B and C
            ("C", "D", "airplane", 10, 10)
        ]
        start_city = "A"
        end_city = "D"
        budget = 50
        time_limit = 50
        # Optimal route avoids unnecessary cycles: A->B, B->C, C->D.
        expected = [("A", "B", "train", 5, 10), ("B", "C", "truck", 5, 10), ("C", "D", "airplane", 10, 10)]
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, {})
        self.assertEqual(result, expected)

    def test_reusing_connection(self):
        # Although connections can be reused, in this scenario the optimal route is straightforward.
        cities = ["A", "B", "C"]
        modes = {"train", "truck", "ship", "airplane"}
        connections = [
            ("A", "B", "train", 3, 5),
            ("B", "A", "train", 3, 5),
            ("B", "C", "truck", 10, 20)
        ]
        start_city = "A"
        end_city = "C"
        budget = 20
        time_limit = 40
        expected = [("A", "B", "train", 3, 5), ("B", "C", "truck", 10, 20)]
        result = route_planner.find_route(cities, modes, connections, start_city, end_city, budget, time_limit, {})
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()