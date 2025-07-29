import unittest
from route_planner import solve

class RoutePlannerTest(unittest.TestCase):
    def test_simple_path(self):
        graph = {
            0: [(1, 10)],
            1: [(0, 10)]
        }
        def get_travel_time(source, dest, time):
            return 10  # constant travel time

        result = solve(graph, 0, 1, 0, 60, get_travel_time)
        self.assertEqual(result, 10)

    def test_multiple_paths(self):
        graph = {
            0: [(1, 10), (2, 15)],
            1: [(0, 10), (3, 20)],
            2: [(0, 15), (3, 30)],
            3: [(1, 20), (2, 30)]
        }
        def get_travel_time(source, dest, time):
            base_times = {
                (0, 1): 10, (1, 0): 10,
                (0, 2): 15, (2, 0): 15,
                (1, 3): 20, (3, 1): 20,
                (2, 3): 30, (3, 2): 30
            }
            return base_times[(source, dest)] + (time % 60) / 10.0

        result = solve(graph, 0, 3, 600, 660, get_travel_time)
        self.assertTrue(620 <= result <= 640)

    def test_no_path_possible(self):
        graph = {
            0: [(1, 10)],
            1: [(0, 10)],
            2: []  # isolated node
        }
        def get_travel_time(source, dest, time):
            return 10

        result = solve(graph, 0, 2, 0, 60, get_travel_time)
        self.assertEqual(result, -1)

    def test_departure_window_constraints(self):
        graph = {
            0: [(1, 10)],
            1: [(0, 10)]
        }
        def get_travel_time(source, dest, time):
            if time >= 100:  # too late to travel
                return float('inf')
            return 10

        result = solve(graph, 0, 1, 101, 120, get_travel_time)
        self.assertEqual(result, -1)

    def test_complex_time_dependent_path(self):
        graph = {
            0: [(1, 10), (2, 20)],
            1: [(0, 10), (2, 15), (3, 30)],
            2: [(0, 20), (1, 15), (3, 25)],
            3: [(1, 30), (2, 25)]
        }
        def get_travel_time(source, dest, time):
            # Simulate heavy traffic during peak hours (time 300-400)
            base_times = {
                (0, 1): 10, (1, 0): 10,
                (0, 2): 20, (2, 0): 20,
                (1, 2): 15, (2, 1): 15,
                (1, 3): 30, (3, 1): 30,
                (2, 3): 25, (3, 2): 25
            }
            base_time = base_times[(source, dest)]
            if 300 <= time <= 400:
                return base_time * 2
            return base_time

        result = solve(graph, 0, 3, 250, 450, get_travel_time)
        self.assertTrue(isinstance(result, (int, float)))
        self.assertTrue(result > 250)

    def test_large_graph(self):
        # Create a larger graph with 50 nodes
        graph = {i: [] for i in range(50)}
        for i in range(49):
            graph[i].append((i + 1, 10))
            graph[i + 1].append((i, 10))

        def get_travel_time(source, dest, time):
            return 10 + (time % 60) / 10.0

        result = solve(graph, 0, 49, 0, 1440, get_travel_time)
        self.assertTrue(isinstance(result, (int, float)))
        self.assertTrue(result >= 490)  # Minimum possible time

    def test_invalid_inputs(self):
        graph = {0: [(1, 10)], 1: [(0, 10)]}
        def get_travel_time(source, dest, time):
            return 10

        # Test invalid departure window
        with self.assertRaises(ValueError):
            solve(graph, 0, 1, 100, 50, get_travel_time)

        # Test non-existent source city
        with self.assertRaises(ValueError):
            solve(graph, 2, 1, 0, 60, get_travel_time)

        # Test non-existent destination city
        with self.assertRaises(ValueError):
            solve(graph, 0, 2, 0, 60, get_travel_time)

if __name__ == '__main__':
    unittest.main()