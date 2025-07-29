import unittest
from meeting_optimizer import find_optimal_meeting_point

class TestMeetingOptimizer(unittest.TestCase):
    def test_empty_team(self):
        # When no team members exist, the expected result is None.
        cities = ["New York", "London", "Tokyo"]
        team_locations = {}  # empty team
        # Dummy get_travel_cost: not used because team is empty.
        def get_travel_cost(city1, city2):
            return 0
        K = 1
        result = find_optimal_meeting_point(cities, team_locations, get_travel_cost, K)
        self.assertIsNone(result)

    def test_all_team_same_city(self):
        # If all team members are in the same city, that city should be chosen.
        cities = ["Paris", "Berlin", "Madrid"]
        team_locations = {1: "Berlin", 2: "Berlin", 3: "Berlin"}
        def get_travel_cost(city1, city2):
            # Dummy cost: 0 if same city; 1 otherwise.
            return 0 if city1 == city2 else 1
        K = 3
        result = find_optimal_meeting_point(cities, team_locations, get_travel_cost, K)
        self.assertEqual(result, "Berlin")

    def test_two_cities_case_K1(self):
        # Two cities with different asymmetric costs.
        cities = ["A", "B"]
        team_locations = {1: "A", 2: "B"}
        def get_travel_cost(city1, city2):
            if city1 == city2:
                return 0
            if city1 == "A" and city2 == "B":
                return 5
            if city1 == "B" and city2 == "A":
                return 7
            return 10
        K = 1
        # For meeting in A: cost = 0 (from A) + 7 (from B) = 7
        # For meeting in B: cost = 5 (from A) + 0 (from B) = 5 --> optimal is B.
        result = find_optimal_meeting_point(cities, team_locations, get_travel_cost, K)
        self.assertEqual(result, "B")

    def test_two_cities_case_K2(self):
        # Use same get_travel_cost as previous test, but with K = 2.
        cities = ["A", "B"]
        team_locations = {1: "A", 2: "B"}
        def get_travel_cost(city1, city2):
            if city1 == city2:
                return 0
            if city1 == "A" and city2 == "B":
                return 5
            if city1 == "B" and city2 == "A":
                return 7
            return 10
        K = 2
        # For meeting in A: cost = (0 + 7)*2 = 14
        # For meeting in B: cost = (5 + 0)*2 = 10 --> optimal is B.
        result = find_optimal_meeting_point(cities, team_locations, get_travel_cost, K)
        self.assertEqual(result, "B")

    def test_three_cities(self):
        # Three cities with non-symmetric travel costs.
        cities = ["A", "B", "C"]
        team_locations = {1: "A", 2: "B", 3: "C"}
        cost_matrix = {
            "A": {"A": 0, "B": 4, "C": 9},
            "B": {"A": 3, "B": 0, "C": 2},
            "C": {"A": 8, "B": 1, "C": 0}
        }
        def get_travel_cost(city1, city2):
            return cost_matrix[city1][city2]
        K = 1
        # Calculate total costs:
        # Meeting in A: 0 (A->A) + 3 (B->A) + 8 (C->A) = 11
        # Meeting in B: 4 (A->B) + 0 (B->B) + 1 (C->B) = 5  --> optimal is B.
        # Meeting in C: 9 (A->C) + 2 (B->C) + 0 (C->C) = 11
        result = find_optimal_meeting_point(cities, team_locations, get_travel_cost, K)
        self.assertEqual(result, "B")

    def test_tie_between_cities(self):
        # Test case where two cities yield the same total cost.
        cities = ["X", "Y"]
        team_locations = {1: "X", 2: "Y"}
        def get_travel_cost(city1, city2):
            if city1 == city2:
                return 0
            return 5
        K = 1
        # For meeting in X: cost = 0 (from X) + 5 (from Y) = 5
        # For meeting in Y: cost = 5 (from X) + 0 (from Y) = 5
        result = find_optimal_meeting_point(cities, team_locations, get_travel_cost, K)
        self.assertIn(result, ["X", "Y"])

if __name__ == '__main__':
    unittest.main()