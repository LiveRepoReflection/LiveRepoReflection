import unittest

from route_optimiser import optimize_routes

def static_traffic_prediction(graph):
    def predict(u, v, current_time):
        # Find the travel time from u to v in the graph.
        if u not in graph:
            raise ValueError(f"No outgoing edges from node {u}")
        for neighbor, travel_time in graph[u]:
            if neighbor == v:
                return travel_time
        raise ValueError(f"Edge from {u} to {v} not found in the graph.")
    return predict

class RouteOptimiserTest(unittest.TestCase):
    def check_route_validity(self, route, depot, required_nodes, traffic_fn, graph):
        # Check that the route is non-empty and starts/ends at the depot.
        self.assertTrue(len(route) >= 2, "Route must contain at least a start and end node.")
        self.assertEqual(route[0][0], depot, "Route must start at the depot.")
        self.assertEqual(route[0][1], 0, "Start time must be 0.")
        self.assertEqual(route[-1][0], depot, "Route must end at the depot.")

        # Collect the intermediate nodes (excluding start and end).
        intermediate_nodes = [node for node, _ in route[1:-1]]
        self.assertEqual(set(intermediate_nodes), set(required_nodes),
                         "The set of intermediate nodes must match the required delivery nodes.")

        # Verify dynamic travel times consistency.
        current_time = 0
        for i in range(1, len(route)):
            prev_node, prev_time = route[i-1]
            curr_node, curr_time = route[i]
            # Use the traffic prediction function to determine expected time increment.
            expected_travel_time = traffic_fn(prev_node, curr_node, prev_time)
            self.assertEqual(curr_time - prev_time, expected_travel_time,
                             f"Travel time from {prev_node} to {curr_node} at time {prev_time} should be {expected_travel_time}.")

    def test_single_vehicle_one_delivery(self):
        # Simple graph with one delivery point.
        graph = {
            0: [(1, 5)],
            1: [(0, 5)]
        }
        vehicle_routes = [[1]]
        depot = 0
        traffic_fn = static_traffic_prediction(graph)
        optimized_routes = optimize_routes(graph, vehicle_routes, depot, traffic_fn)
        
        self.assertEqual(len(optimized_routes), 1, "There should be one route for one vehicle.")
        route = optimized_routes[0]
        expected_route = [[0, 0], [1, 5], [0, 10]]
        self.assertEqual(route, expected_route, "The route does not match the expected outcome.")

    def test_single_vehicle_empty_route(self):
        # Test a vehicle with no delivery points.
        graph = {
            0: [(0, 0)]
        }
        vehicle_routes = [[]]
        depot = 0
        # Define a traffic function that always returns 0,
        # since there's no travel between nodes.
        def constant_traffic(u, v, current_time):
            return 0
        optimized_routes = optimize_routes(graph, vehicle_routes, depot, constant_traffic)
        
        self.assertEqual(len(optimized_routes), 1, "There should be one route for one vehicle.")
        route = optimized_routes[0]
        expected_route = [[0, 0], [0, 0]]
        self.assertEqual(route, expected_route, "Empty delivery route should return immediately to the depot.")

    def test_multiple_vehicles(self):
        # Graph with multiple nodes and vehicles.
        graph = {
            0: [(1, 10), (2, 15), (3, 20)],
            1: [(0, 10), (2, 9), (3, 12)],
            2: [(0, 15), (1, 9), (3, 8)],
            3: [(0, 20), (1, 12), (2, 8)]
        }
        vehicle_routes = [
            [1, 2],
            [3]
        ]
        depot = 0
        traffic_fn = static_traffic_prediction(graph)
        optimized_routes = optimize_routes(graph, vehicle_routes, depot, traffic_fn)
        
        self.assertEqual(len(optimized_routes), 2, "There should be two routes for two vehicles.")
        
        # Validate each route's structure and dynamic timing.
        # For vehicle 1:
        route_vehicle1 = optimized_routes[0]
        self.check_route_validity(route_vehicle1, depot, [1, 2], traffic_fn, graph)
        
        # For vehicle 2:
        route_vehicle2 = optimized_routes[1]
        self.check_route_validity(route_vehicle2, depot, [3], traffic_fn, graph)

    def test_dynamic_time_consistency(self):
        # Graph with varying travel times, ensuring that dynamic travel times are computed correctly.
        graph = {
            0: [(1, 7), (2, 14)],
            1: [(0, 7), (2, 3)],
            2: [(0, 14), (1, 3)]
        }
        vehicle_routes = [[1, 2]]
        depot = 0
        traffic_fn = static_traffic_prediction(graph)
        optimized_routes = optimize_routes(graph, vehicle_routes, depot, traffic_fn)
        
        self.assertEqual(len(optimized_routes), 1, "There should be one route for the single vehicle.")
        route = optimized_routes[0]
        self.check_route_validity(route, depot, [1, 2], traffic_fn, graph)

    def test_missing_edge_exception(self):
        # Test a scenario where a required edge is missing in the graph.
        graph = {
            0: [(1, 10)],
            1: []  # Missing edge from 1 back to 0 or to any other node.
        }
        vehicle_routes = [[1]]
        depot = 0
        traffic_fn = static_traffic_prediction(graph)
        with self.assertRaises(ValueError):
            optimize_routes(graph, vehicle_routes, depot, traffic_fn)

if __name__ == '__main__':
    unittest.main()