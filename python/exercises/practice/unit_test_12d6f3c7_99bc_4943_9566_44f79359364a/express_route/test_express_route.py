import unittest
from express_route.express_route import optimize_network

class TestExpressRoute(unittest.TestCase):
    def test_basic_route(self):
        # Scenario: two cities with one direct route.
        # There are 100 passengers from city 0 to 1.
        # With a train capacity of 50 and SLA 100%, we need 2 trains.
        # Rail line cost: 2.0 * 60 = 120 per train; total rail cost = 120 * 2 = 240.
        # Fixed cost: 1000 per train; total fixed cost = 1000 * 2 = 2000.
        # Overall expected cost = 240 + 2000 = 2240.
        N = 2
        graph = [
            (0, 1, 60, 2.0, 10)
        ]
        demand = [
            [0, 100],
            [0, 0]
        ]
        time_windows = [
            [(0, 120), (0, 120)],
            [(0, 120), (0, 120)]
        ]
        train_capacity = 50
        SLA_percentage = 1.0
        fixed_cost_per_train = 1000

        expected = 2240.0
        result = optimize_network(N, graph, demand, train_capacity, time_windows, SLA_percentage, fixed_cost_per_train)
        self.assertAlmostEqual(result, expected, places=2)

    def test_no_solution(self):
        # Scenario: three cities but with no connection to satisfy demand for one city pair.
        # Graph has only one edge from 0 -> 1.
        # Demand exists from city 0 -> 2, but no route exists; expected result: -1.0.
        N = 3
        graph = [
            (0, 1, 60, 2.0, 10)
        ]
        demand = [
            [0, 50, 30],
            [0, 0, 40],
            [20, 10, 0]
        ]
        time_windows = [
            [(0, 120), (0, 120), (0, 120)],
            [(0, 120), (0, 120), (0, 120)],
            [(0, 120), (0, 120), (0, 120)]
        ]
        train_capacity = 50
        SLA_percentage = 1.0
        fixed_cost_per_train = 1000

        expected = -1.0
        result = optimize_network(N, graph, demand, train_capacity, time_windows, SLA_percentage, fixed_cost_per_train)
        self.assertEqual(result, expected)

    def test_multiple_paths(self):
        # Scenario: three cities with two possible paths from city 0 to 2:
        # 1. Direct route: 0 -> 2: travel_time=120, cost=1.5 per minute, capacity=3
        #    Cost per train = 1.5 * 120 = 180.
        # 2. Indirect route: 0 -> 1 -> 2:
        #    Cost = (0->1: 60*3.0=180) + (1->2: 30*2.0=60) = 240 per train.
        # With 90 passengers from 0 to 2 and train_capacity=50 with SLA 100%,
        # 2 trains are required. The optimal is the direct route:
        # Total cost = (2 * 180) + (2 * 800) = 360 + 1600 = 1960.
        N = 3
        graph = [
            (0, 1, 60, 3.0, 5),
            (0, 2, 120, 1.5, 3),
            (1, 2, 30, 2.0, 10)
        ]
        demand = [
            [0, 0, 90],
            [0, 0, 0],
            [0, 0, 0]
        ]
        time_windows = [
            [(0, 200), (0, 200), (0, 200)],
            [(0, 200), (0, 200), (0, 200)],
            [(0, 200), (0, 200), (0, 200)]
        ]
        train_capacity = 50
        SLA_percentage = 1.0
        fixed_cost_per_train = 800

        expected = 1960.0
        result = optimize_network(N, graph, demand, train_capacity, time_windows, SLA_percentage, fixed_cost_per_train)
        self.assertAlmostEqual(result, expected, places=2)

if __name__ == '__main__':
    unittest.main()