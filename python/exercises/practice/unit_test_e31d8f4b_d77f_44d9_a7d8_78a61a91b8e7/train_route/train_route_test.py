import unittest
from train_route import find_optimal_route

class TestTrainRoute(unittest.TestCase):
    def test_direct_route(self):
        # Simple direct route between two cities, satisfying constraints.
        cities = ["A", "B"]
        tracks = [
            {
                "start_city": "A",
                "end_city": "B",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 50.0,
                "is_scenic": False
            }
        ]
        start_city = "A"
        destination_city = "B"
        budget = 100.0
        time_limit = 2.0  # 100/100 = 1 hour
        penalty = 5.0
        expected_route = ["A", "B"]
        result = find_optimal_route(cities, tracks, start_city, destination_city, budget, time_limit, penalty)
        self.assertEqual(result, expected_route)

    def test_indirect_route_with_penalty(self):
        # Two possible routes:
        # Direct route A->C: time = 120/60 = 2 hrs, cost = 80. 
        # Indirect route A->B->C: times: A->B: 50/50=1 hr, B->C: 50/50=1 hr, cost = 20+20, penalty for city B = 5.
        # With budget = 50, only indirect route is possible.
        cities = ["A", "B", "C"]
        tracks = [
            {
                "start_city": "A",
                "end_city": "B",
                "length": 50.0,
                "speed_limit": 50.0,
                "maintenance_cost": 20.0,
                "is_scenic": True
            },
            {
                "start_city": "B",
                "end_city": "C",
                "length": 50.0,
                "speed_limit": 50.0,
                "maintenance_cost": 20.0,
                "is_scenic": True
            },
            {
                "start_city": "A",
                "end_city": "C",
                "length": 120.0,
                "speed_limit": 60.0,
                "maintenance_cost": 80.0,
                "is_scenic": False
            }
        ]
        start_city = "A"
        destination_city = "C"
        budget = 50.0
        time_limit = 3.0  # indirect route takes 2 hours, direct takes 2 hours as well but exceeds budget.
        penalty = 5.0
        expected_route = ["A", "B", "C"]
        result = find_optimal_route(cities, tracks, start_city, destination_city, budget, time_limit, penalty)
        self.assertEqual(result, expected_route)

    def test_scenic_tiebreaker(self):
        # Two routes with same travel time and same overall cost, but different number of scenic tracks.
        # Route1: A -> B -> D (A->B and B->D are scenic)
        # Route2: A -> C -> D (non-scenic tracks)
        # Both routes: total travel time = 1 + 1 = 2 hrs and base cost = 20+20 with penalty for intermediate city.
        # With a tie in time and cost, the route with more scenic tracks (route1) should be chosen.
        cities = ["A", "B", "C", "D"]
        tracks = [
            {
                "start_city": "A",
                "end_city": "B",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 20.0,
                "is_scenic": True
            },
            {
                "start_city": "B",
                "end_city": "D",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 20.0,
                "is_scenic": True
            },
            {
                "start_city": "A",
                "end_city": "C",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 20.0,
                "is_scenic": False
            },
            {
                "start_city": "C",
                "end_city": "D",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 20.0,
                "is_scenic": False
            }
        ]
        start_city = "A"
        destination_city = "D"
        budget = 60.0  # Both routes' cost: (20+20 + penalty 10) = 50.
        time_limit = 3.0
        penalty = 10.0
        expected_route = ["A", "B", "D"]
        result = find_optimal_route(cities, tracks, start_city, destination_city, budget, time_limit, penalty)
        self.assertEqual(result, expected_route)

    def test_no_route_due_to_budget(self):
        # Design a scenario where no route exists under the given budget.
        cities = ["A", "B", "C"]
        tracks = [
            {
                "start_city": "A",
                "end_city": "B",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 80.0,
                "is_scenic": False
            },
            {
                "start_city": "B",
                "end_city": "C",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 80.0,
                "is_scenic": False
            },
            {
                "start_city": "A",
                "end_city": "C",
                "length": 200.0,
                "speed_limit": 100.0,
                "maintenance_cost": 150.0,
                "is_scenic": True
            }
        ]
        start_city = "A"
        destination_city = "C"
        budget = 100.0  # Neither route can satisfy the budget constraint.
        time_limit = 3.0
        penalty = 5.0
        expected_route = []
        result = find_optimal_route(cities, tracks, start_city, destination_city, budget, time_limit, penalty)
        self.assertEqual(result, expected_route)

    def test_no_route_due_to_time(self):
        # Scenario where all available routes exceed the time limit.
        cities = ["A", "B", "C"]
        tracks = [
            {
                "start_city": "A",
                "end_city": "B",
                "length": 400.0,
                "speed_limit": 100.0,
                "maintenance_cost": 30.0,
                "is_scenic": True
            },
            {
                "start_city": "B",
                "end_city": "C",
                "length": 400.0,
                "speed_limit": 100.0,
                "maintenance_cost": 30.0,
                "is_scenic": True
            },
            {
                "start_city": "A",
                "end_city": "C",
                "length": 800.0,
                "speed_limit": 100.0,
                "maintenance_cost": 50.0,
                "is_scenic": False
            }
        ]
        start_city = "A"
        destination_city = "C"
        budget = 200.0
        time_limit = 7.0  # Indirect route takes 8 hrs; direct route takes 8 hrs.
        penalty = 5.0
        expected_route = []
        result = find_optimal_route(cities, tracks, start_city, destination_city, budget, time_limit, penalty)
        self.assertEqual(result, expected_route)

    def test_cycle_detection(self):
        # Scenario with potential cycles. The route should not revisit any city.
        cities = ["A", "B", "C"]
        tracks = [
            {
                "start_city": "A",
                "end_city": "B",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 20.0,
                "is_scenic": False
            },
            {
                "start_city": "B",
                "end_city": "A",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 20.0,
                "is_scenic": False
            },
            {
                "start_city": "B",
                "end_city": "C",
                "length": 100.0,
                "speed_limit": 100.0,
                "maintenance_cost": 20.0,
                "is_scenic": True
            }
        ]
        start_city = "A"
        destination_city = "C"
        budget = 100.0
        time_limit = 3.0
        penalty = 5.0
        # Optimal route should be A -> B -> C without revisiting A.
        expected_route = ["A", "B", "C"]
        result = find_optimal_route(cities, tracks, start_city, destination_city, budget, time_limit, penalty)
        self.assertEqual(result, expected_route)

if __name__ == '__main__':
    unittest.main()