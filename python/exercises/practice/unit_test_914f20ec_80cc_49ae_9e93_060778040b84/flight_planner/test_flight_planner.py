import unittest
from flight_planner.flight_planner import solve_flight_planner

class TestFlightPlanner(unittest.TestCase):
    def test_single_flight_path(self):
        n = 3
        flights = [(0, 1, 10), (1, 2, 20)]
        queries = [(0, 2, 2, 30)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [30])

    def test_no_path_exists(self):
        n = 4
        flights = [(0, 1, 10), (2, 3, 20)]
        queries = [(0, 3, 3, 100)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [-1])

    def test_multiple_paths_with_constraints(self):
        n = 5
        flights = [(0, 1, 10), (0, 2, 15), (1, 3, 12), (2, 3, 8), (3, 4, 5)]
        queries = [(0, 4, 3, 30), (0, 4, 2, 25), (1, 4, 1, 10)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [27, -1, -1])

    def test_cycle_in_graph(self):
        n = 4
        flights = [(0, 1, 5), (1, 2, 5), (2, 0, 5), (2, 3, 10)]
        queries = [(0, 3, 3, 25), (0, 3, 10, 25)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [20, 20])

    def test_multiple_flights_same_route(self):
        n = 3
        flights = [(0, 1, 10), (0, 1, 5), (1, 2, 10)]
        queries = [(0, 2, 2, 20)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [15])

    def test_max_flights_constraint(self):
        n = 4
        flights = [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
        queries = [(0, 3, 2, 10), (0, 3, 3, 10)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [-1, 3])

    def test_max_cost_constraint(self):
        n = 3
        flights = [(0, 1, 10), (1, 2, 10)]
        queries = [(0, 2, 2, 15)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [-1])

    def test_large_number_of_airports(self):
        n = 100
        flights = [(i, i+1, 1) for i in range(99)]
        queries = [(0, 99, 100, 100), (0, 99, 50, 100)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [99, -1])

    def test_same_start_and_end(self):
        n = 3
        flights = [(0, 1, 10), (1, 2, 20)]
        queries = [(0, 0, 0, 0), (0, 0, 1, 10)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [0, 0])

    def test_empty_flights(self):
        n = 2
        flights = []
        queries = [(0, 1, 1, 10)]
        self.assertEqual(solve_flight_planner(n, flights, queries), [-1])

if __name__ == '__main__':
    unittest.main()