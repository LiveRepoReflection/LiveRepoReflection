import unittest
import math

from auto_fleet_route import route_vehicles

def congestion_linear(num_vehicles):
    return 1 + 0.1 * num_vehicles

def congestion_constant(num_vehicles):
    return 1

class AutoFleetRouteTests(unittest.TestCase):
    def test_single_vehicle_direct_path(self):
        # Graph with a direct edge from 1 to 2.
        city_graph = {
            1: [(2, 10, congestion_constant)],
            2: []
        }
        vehicles = [(1, 2)]
        routes, max_travel_time = route_vehicles(city_graph, vehicles)
        self.assertEqual(routes[0], [1, 2])
        self.assertEqual(max_travel_time, 10)

    def test_unreachable_destination(self):
        # Graph where destination is unreachable.
        city_graph = {
            1: [(2, 10, congestion_constant)],
            2: [],
            3: []
        }
        vehicles = [(1, 3)]
        routes, max_travel_time = route_vehicles(city_graph, vehicles)
        self.assertEqual(routes[0], [])
        self.assertEqual(max_travel_time, float('inf'))

    def test_multiple_vehicles_same_route(self):
        # Graph with a sequential path from 1->2->3->4.
        city_graph = {
            1: [(2, 5, congestion_linear)],
            2: [(3, 5, congestion_linear)],
            3: [(4, 5, congestion_linear)],
            4: []
        }
        vehicles = [(1, 4), (1, 4)]
        routes, max_travel_time = route_vehicles(city_graph, vehicles)
        for route in routes:
            self.assertEqual(route, [1, 2, 3, 4])
        # Each edge's travel time becomes: 5 * (1 + 0.1*2) = 6.0, total time: 18.0.
        self.assertAlmostEqual(max_travel_time, 18.0)

    def test_multiple_paths_choose_optimal(self):
        # Graph with two possible routes:
        # Route 1: 1 -> 2 -> 4 with travel time = 5 + 20 = 25.
        # Route 2: 1 -> 3 -> 4 with travel time = 10 + 10 = 20.
        city_graph = {
            1: [(2, 5, congestion_constant), (3, 10, congestion_constant)],
            2: [(4, 20, congestion_constant)],
            3: [(4, 10, congestion_constant)],
            4: []
        }
        vehicles = [(1, 4)]
        routes, max_travel_time = route_vehicles(city_graph, vehicles)
        self.assertEqual(routes[0], [1, 3, 4])
        self.assertEqual(max_travel_time, 20)

    def test_cycle_graph(self):
        # Graph that contains a cycle; algorithm must avoid infinite loops.
        city_graph = {
            1: [(2, 5, congestion_constant)],
            2: [(3, 5, congestion_constant)],
            3: [(1, 5, congestion_constant), (4, 10, congestion_constant)],
            4: []
        }
        vehicles = [(1, 4)]
        routes, max_travel_time = route_vehicles(city_graph, vehicles)
        self.assertEqual(routes[0], [1, 2, 3, 4])
        self.assertEqual(max_travel_time, 20)

    def test_large_graph_efficiency(self):
        # Build a linear graph: 1->2->...->101.
        city_graph = {}
        n = 101
        for i in range(1, n):
            city_graph[i] = [(i + 1, 1, congestion_constant)]
        city_graph[n] = []
        vehicles = [(1, n)] * 10  # 10 vehicles on the same route.
        routes, max_travel_time = route_vehicles(city_graph, vehicles)
        expected_route = list(range(1, n + 1))
        for route in routes:
            self.assertEqual(route, expected_route)
        self.assertEqual(max_travel_time, 100)

if __name__ == '__main__':
    unittest.main()