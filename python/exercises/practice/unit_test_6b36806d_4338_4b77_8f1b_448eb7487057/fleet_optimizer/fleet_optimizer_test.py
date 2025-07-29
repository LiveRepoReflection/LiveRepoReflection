import unittest
from fleet_optimizer import plan_routes

def is_valid_route(route, origin, destination, graph):
    if not route or route[0] != origin or route[-1] != destination:
        return False
    for i in range(len(route) - 1):
        current = route[i]
        next_node = route[i + 1]
        neighbors = [edge[0] for edge in graph.get(current, [])]
        if next_node not in neighbors:
            return False
    return True

def congestion_factor_example(start_node, end_node, time):
    # Simple linear congestion increase
    return 1.0 + (time / 3600.0)

class FleetOptimizerTest(unittest.TestCase):
    def test_single_route_validity(self):
        # Simple graph with a clear valid path from 0 to 3
        city_graph = {
            0: [(1, 60, 5), (2, 100, 8)],
            1: [(3, 80, 4)],
            2: [(3, 60, 3)],
            3: []
        }
        av_requests = [
            (0, 3, 0, 5)  # origin, destination, departure_time, priority
        ]
        max_avs = 2
        total_energy_budget = 10000  # ample energy budget
        routes = plan_routes(city_graph, congestion_factor_example, av_requests, max_avs, total_energy_budget)
        self.assertIsNotNone(routes, "Expected a valid routing solution.")
        self.assertEqual(len(routes), len(av_requests), "Number of routes should match number of requests.")
        # Validate each route
        for req, route in zip(av_requests, routes):
            origin, destination, _, _ = req
            self.assertTrue(is_valid_route(route, origin, destination, city_graph),
                            f"Route {route} is not a valid path from {origin} to {destination}.")

    def test_multiple_requests(self):
        city_graph = {
            0: [(1, 60, 5), (2, 80, 4)],
            1: [(3, 60, 3)],
            2: [(3, 50, 4)],
            3: [(4, 70, 6)],
            4: []
        }
        av_requests = [
            (0, 4, 0, 7),  # High priority, must be handled in a timely manner.
            (2, 4, 10, 5)  # Lower priority.
        ]
        max_avs = 2
        total_energy_budget = 20000
        routes = plan_routes(city_graph, congestion_factor_example, av_requests, max_avs, total_energy_budget)
        self.assertIsNotNone(routes, "Expected a valid routing solution for multiple requests.")
        self.assertEqual(len(routes), len(av_requests), "Each AV request should have an associated route.")
        for req, route in zip(av_requests, routes):
            origin, destination, _, _ = req
            self.assertTrue(is_valid_route(route, origin, destination, city_graph),
                            f"Route {route} is not a valid path from {origin} to {destination}.")

    def test_no_possible_route(self):
        # Graph where destination is unreachable from origin
        city_graph = {
            0: [(1, 60, 5)],
            1: [],
            2: []  # Node 2 is disconnected
        }
        av_requests = [
            (0, 2, 0, 3)
        ]
        max_avs = 1
        total_energy_budget = 10000
        routes = plan_routes(city_graph, congestion_factor_example, av_requests, max_avs, total_energy_budget)
        self.assertIsNone(routes, "Expected None when no feasible route exists.")

    def test_resource_limit_exceeded(self):
        # Even if a route exists, the energy budget is too low to allow any travel.
        city_graph = {
            0: [(1, 60, 5), (2, 100, 8)],
            1: [(3, 80, 4)],
            2: [(3, 60, 3)],
            3: []
        }
        av_requests = [
            (0, 3, 0, 5)
        ]
        max_avs = 1
        total_energy_budget = 10  # Energy budget too low for any valid route
        routes = plan_routes(city_graph, congestion_factor_example, av_requests, max_avs, total_energy_budget)
        self.assertIsNone(routes, "Expected None when total energy budget is insufficient.")

    def test_congestion_effects(self):
        # Testing to observe the effect of congestion factor on routing
        city_graph = {
            0: [(1, 60, 5), (2, 120, 3)],
            1: [(3, 90, 4)],
            2: [(3, 60, 2)],
            3: []
        }
        # Custom congestion function increasing congestion sharply after 1800 seconds
        def custom_congestion(start_node, end_node, time):
            if time < 1800:
                return 1.0
            return 2.0  # double the effect after 1800 seconds

        av_requests = [
            (0, 3, 0, 6),    # early departure, no extra congestion
            (0, 3, 2000, 8)  # departure after heavy congestion starts
        ]
        max_avs = 2
        total_energy_budget = 15000
        routes = plan_routes(city_graph, custom_congestion, av_requests, max_avs, total_energy_budget)
        self.assertIsNotNone(routes, "Expected valid routes even with congestion effects.")
        self.assertEqual(len(routes), len(av_requests))
        for req, route in zip(av_requests, routes):
            origin, destination, _, _ = req
            self.assertTrue(is_valid_route(route, origin, destination, city_graph),
                            f"Route {route} is not valid from {origin} to {destination} with congestion effects.")

if __name__ == "__main__":
    unittest.main()