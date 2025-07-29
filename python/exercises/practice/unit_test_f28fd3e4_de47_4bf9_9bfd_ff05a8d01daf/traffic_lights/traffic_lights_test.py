import unittest
from itertools import combinations
import math

from traffic_lights import traffic_lights

def compute_average_travel_time(n, roads, delay_function, lights):
    # Initialize matrix of travel times using infinity as placeholder
    times = [[math.inf for _ in range(n)] for _ in range(n)]
    for i in range(n):
        times[i][i] = 0.0
    # Set direct travel times based on roads and installed traffic lights
    for (u, v, length, speed_limit) in roads:
        base_time = length / speed_limit
        extra_delay = delay_function(length, speed_limit) if v in lights else 0.0
        travel_time = base_time + extra_delay
        if travel_time < times[u][v]:
            times[u][v] = travel_time
    # Run Floyd-Warshall to compute shortest travel times over all pairs
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if times[i][k] + times[k][j] < times[i][j]:
                    times[i][j] = times[i][k] + times[k][j]
    total_time = 0.0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j and times[i][j] < math.inf:
                total_time += times[i][j]
                count += 1
    return total_time / count if count > 0 else math.inf

def brute_force_optimal(n, roads, delay_function, max_lights):
    best_avg = math.inf
    best_set = []
    vertices = list(range(n))
    # Consider all subsets of intersections of size 0 up to max_lights
    for r in range(0, max_lights + 1):
        for subset in combinations(vertices, r):
            avg_time = compute_average_travel_time(n, roads, delay_function, set(subset))
            if avg_time < best_avg:
                best_avg = avg_time
                best_set = list(subset)
    return best_avg, best_set

class TrafficLightsTest(unittest.TestCase):
    def setUp(self):
        self.tolerance = 1e-6

    def test_budget_zero(self):
        n = 3
        roads = [
            (0, 1, 100, 10),
            (1, 2, 50, 5),
            (2, 0, 200, 20)
        ]
        budget = 0
        light_cost = 1
        delay_function = lambda length, speed: length / (2 * speed)
        result = traffic_lights(n, roads, budget, light_cost, delay_function)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_simple_cycle(self):
        n = 3
        roads = [
            (0, 1, 100, 10),
            (1, 2, 50, 5),
            (2, 0, 200, 20)
        ]
        budget = 1
        light_cost = 1
        delay_function = lambda length, speed: length / (2 * speed)
        optimal_avg, _ = brute_force_optimal(n, roads, delay_function, budget)
        candidate = traffic_lights(n, roads, budget, light_cost, delay_function)
        self.assertLessEqual(len(candidate), budget)
        candidate_avg = compute_average_travel_time(n, roads, delay_function, set(candidate))
        self.assertAlmostEqual(candidate_avg, optimal_avg, delta=self.tolerance)

    def test_multiple_lights(self):
        n = 4
        roads = [
            (0, 1, 100, 10),
            (1, 2, 150, 15),
            (2, 3, 120, 12),
            (3, 0, 200, 20),
            (0, 2, 300, 30),
            (1, 3, 250, 25)
        ]
        budget = 2
        light_cost = 1
        delay_function = lambda length, speed: length / (3 * speed)
        optimal_avg, _ = brute_force_optimal(n, roads, delay_function, budget)
        candidate = traffic_lights(n, roads, budget, light_cost, delay_function)
        self.assertLessEqual(len(candidate), budget)
        candidate_avg = compute_average_travel_time(n, roads, delay_function, set(candidate))
        self.assertAlmostEqual(candidate_avg, optimal_avg, delta=self.tolerance)

    def test_disconnected_graph(self):
        n = 4
        # Two disconnected components: one between 0 and 1, and another between 2 and 3
        roads = [
            (0, 1, 100, 10),
            (1, 0, 100, 10),
            (2, 3, 200, 20),
            (3, 2, 200, 20)
        ]
        budget = 2
        light_cost = 1
        delay_function = lambda length, speed: length / (2 * speed)
        optimal_avg, _ = brute_force_optimal(n, roads, delay_function, budget)
        candidate = traffic_lights(n, roads, budget, light_cost, delay_function)
        self.assertLessEqual(len(candidate), budget)
        candidate_avg = compute_average_travel_time(n, roads, delay_function, set(candidate))
        self.assertAlmostEqual(candidate_avg, optimal_avg, delta=self.tolerance)

    def test_no_improvement(self):
        n = 3
        # In this graph, adding traffic lights does not introduce additional delay
        roads = [
            (0, 1, 100, 10),
            (1, 2, 100, 10),
            (2, 0, 100, 10)
        ]
        budget = 2
        light_cost = 1
        delay_function = lambda length, speed: 0.0
        optimal_avg, _ = brute_force_optimal(n, roads, delay_function, budget)
        candidate = traffic_lights(n, roads, budget, light_cost, delay_function)
        candidate_avg = compute_average_travel_time(n, roads, delay_function, set(candidate))
        self.assertLessEqual(len(candidate), budget)
        self.assertAlmostEqual(candidate_avg, optimal_avg, delta=self.tolerance)

if __name__ == '__main__':
    unittest.main()