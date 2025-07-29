import unittest
from traffic_optimizer import optimize_traffic_lights

class TestTrafficOptimizer(unittest.TestCase):
    def test_simple_intersection(self):
        N = 2
        M = 1
        roads = [(0, 1, 100, 10)]
        K = 1
        lights = [0]
        max_cycle_time = 60
        arrival_times = [(0, [0, 1])]
        result = optimize_traffic_lights(N, M, roads, K, lights, max_cycle_time, arrival_times)
        self.assertEqual(len(result), 1)
        self.assertTrue(0 <= result[0] <= max_cycle_time)

    def test_multiple_intersections(self):
        N = 3
        M = 3
        roads = [(0, 1, 100, 10), (1, 2, 200, 20), (0, 2, 300, 30)]
        K = 2
        lights = [0, 1]
        max_cycle_time = 120
        arrival_times = [(0, [0, 1, 2]), (30, [0, 2])]
        result = optimize_traffic_lights(N, M, roads, K, lights, max_cycle_time, arrival_times)
        self.assertEqual(len(result), 2)
        for duration in result:
            self.assertTrue(0 <= duration <= max_cycle_time)

    def test_complex_network(self):
        N = 4
        M = 5
        roads = [(0, 1, 100, 10), (1, 2, 150, 15), (2, 3, 200, 20), 
                (0, 2, 300, 30), (1, 3, 250, 25)]
        K = 3
        lights = [0, 1, 2]
        max_cycle_time = 180
        arrival_times = [(0, [0, 1, 3]), (15, [0, 2, 3]), (45, [1, 2, 3])]
        result = optimize_traffic_lights(N, M, roads, K, lights, max_cycle_time, arrival_times)
        self.assertEqual(len(result), 3)
        for duration in result:
            self.assertTrue(0 <= duration <= max_cycle_time)

    def test_edge_case_empty_arrivals(self):
        N = 2
        M = 1
        roads = [(0, 1, 100, 10)]
        K = 1
        lights = [0]
        max_cycle_time = 60
        arrival_times = []
        result = optimize_traffic_lights(N, M, roads, K, lights, max_cycle_time, arrival_times)
        self.assertEqual(len(result), 1)
        self.assertTrue(0 <= result[0] <= max_cycle_time)

    def test_max_cycle_constraint(self):
        N = 3
        M = 2
        roads = [(0, 1, 100, 10), (1, 2, 200, 20)]
        K = 1
        lights = [1]
        max_cycle_time = 30
        arrival_times = [(0, [0, 1, 2]), (15, [1, 2])]
        result = optimize_traffic_lights(N, M, roads, K, lights, max_cycle_time, arrival_times)
        self.assertEqual(len(result), 1)
        self.assertTrue(0 <= result[0] <= max_cycle_time)

if __name__ == '__main__':
    unittest.main()