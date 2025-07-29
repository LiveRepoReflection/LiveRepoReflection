import unittest
from route_optimize import min_vehicles_required

class TestRouteOptimize(unittest.TestCase):
    def test_single_request(self):
        # A simple test with a single delivery request.
        N = 3
        graph = {
            0: {1: 5, 2: 10},
            1: {2: 5},
            2: {}
        }
        requests = [(0, 1, 5)]
        C = 10
        T = 10
        expected = 1
        result = min_vehicles_required(N, graph, requests, C, T)
        self.assertEqual(result, expected)

    def test_example_case(self):
        # Test using the example provided in the problem description.
        N = 5
        graph = {
            0: {1: 10, 2: 15},
            1: {3: 20},
            2: {4: 25},
            3: {4: 10},
            4: {}
        }
        requests = [(0, 1, 5), (2, 3, 10), (1, 4, 15)]
        C = 20
        T = 60
        expected = 2
        result = min_vehicles_required(N, graph, requests, C, T)
        self.assertEqual(result, expected)

    def test_multiple_requests_same_route(self):
        # Multiple requests with identical source and destination that can be combined.
        N = 4
        graph = {
            0: {1: 10},
            1: {2: 10},
            2: {3: 10},
            3: {}
        }
        requests = [(0, 3, 3), (0, 3, 4), (0, 3, 2)]
        C = 10
        T = 40  # The travel time (0 -> 1 -> 2 -> 3) is 30.
        expected = 1
        result = min_vehicles_required(N, graph, requests, C, T)
        self.assertEqual(result, expected)

    def test_capacity_constraint(self):
        # Even though the travel route fits within the time limit,
        # the capacity constraint forces splitting the requests between vehicles.
        N = 4
        graph = {
            0: {1: 5},
            1: {2: 5},
            2: {3: 5},
            3: {}
        }
        requests = [(0, 3, 6), (0, 3, 6)]
        C = 10
        T = 30
        expected = 2
        result = min_vehicles_required(N, graph, requests, C, T)
        self.assertEqual(result, expected)

    def test_time_constraint(self):
        # The travel time between the required points exceeds the time limit if combined.
        N = 4
        graph = {
            0: {1: 15},
            1: {2: 15},
            2: {3: 15},
            3: {}
        }
        requests = [(0, 3, 5), (0, 3, 5)]
        C = 15
        T = 40  # The shortest path takes 45 minutes, so each request must be served separately.
        expected = 2
        result = min_vehicles_required(N, graph, requests, C, T)
        self.assertEqual(result, expected)

    def test_complex_case(self):
        # A more complex scenario with a branching graph and multiple requests.
        N = 6
        graph = {
            0: {1: 10, 2: 20},
            1: {3: 10, 4: 30},
            2: {4: 5, 5: 15},
            3: {5: 10},
            4: {5: 5},
            5: {}
        }
        requests = [(0, 3, 4), (0, 4, 5), (2, 5, 3), (1, 5, 2)]
        C = 10
        T = 50
        # Expected value is determined by the ability to combine some routes under capacity and time constraints.
        expected = 2
        result = min_vehicles_required(N, graph, requests, C, T)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()