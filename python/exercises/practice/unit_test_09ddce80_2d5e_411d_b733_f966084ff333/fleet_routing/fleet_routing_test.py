import unittest
from collections import defaultdict

try:
    from fleet_routing import solve
except ImportError as e:
    raise ImportError("Cannot import function 'solve' from module 'fleet_routing'. Make sure your file is named fleet_routing.py and contains the solve function.") from e

class FleetRoutingTestCase(unittest.TestCase):
    
    def validate_route(self, routes, vehicle_start_locations):
        # Check that we have a route for every vehicle.
        self.assertEqual(len(routes), len(vehicle_start_locations), 
                         "The number of routes should equal the number of vehicles.")

        for idx, route in enumerate(routes):
            # Check route is a list
            self.assertIsInstance(route, list, f"Route for vehicle {idx} should be a list.")
            # Check first instruction starts at vehicle's start location
            self.assertGreaterEqual(len(route), 1, f"Route for vehicle {idx} should not be empty.")
            first_instruction = route[0]
            self.assertEqual(first_instruction[0], vehicle_start_locations[idx],
                             f"Vehicle {idx} should start at its designated start location.")
            # Check that times are non-decreasing and each instruction is valid
            prev_time = -1
            for instruction in route:
                self.assertIsInstance(instruction, tuple, "Each instruction should be a tuple.")
                self.assertEqual(len(instruction), 4, "Each instruction tuple must have exactly 4 elements.")
                node_id, time, action, package_id = instruction
                self.assertIsInstance(node_id, int, "node_id must be an integer.")
                self.assertIsInstance(time, int, "time must be an integer.")
                self.assertIsInstance(action, str, "action must be a string.")
                self.assertIsInstance(package_id, int, "package_id must be an integer.")
                # Check time non-decreasing
                self.assertGreaterEqual(time, prev_time, "Times in a route should be non-decreasing.")
                prev_time = time
                # Validate action field
                self.assertIn(action, ["idle", "pickup", "dropoff", "charge"],
                              f"Invalid action '{action}' in route; must be one of 'idle', 'pickup', 'dropoff', 'charge'.")
                # If action is idle or charge, package_id must be -1
                if action in ["idle", "charge"]:
                    self.assertEqual(package_id, -1, "For 'idle' or 'charge' actions, package_id must be -1.")
                else:
                    self.assertNotEqual(package_id, -1, "For 'pickup' or 'dropoff', package_id should not be -1.")
    
    def validate_delivery_coverage(self, routes, delivery_requests):
        # Collect pickups and dropoffs for each package_id
        pickup_count = defaultdict(int)
        dropoff_count = defaultdict(int)
        for route in routes:
            for instruction in route:
                _, _, action, package_id = instruction
                if action == "pickup":
                    pickup_count[package_id] += 1
                elif action == "dropoff":
                    dropoff_count[package_id] += 1
        # Each delivery request should have exactly one pickup and one dropoff across all vehicles
        for pkg_id in range(len(delivery_requests)):
            self.assertEqual(pickup_count[pkg_id], 1, f"Package {pkg_id} must be picked up exactly once.")
            self.assertEqual(dropoff_count[pkg_id], 1, f"Package {pkg_id} must be dropped off exactly once.")

    def test_single_vehicle_single_request(self):
        # Graph: 1 -> 2 -> 3
        graph = {
            1: [(2, 1)],
            2: [(3, 1)],
            3: []
        }
        N = 1
        M = 1
        vehicle_start_locations = [1]
        # delivery request defined as (pickup_node, dropoff_node, package_size, time_window_start, time_window_end)
        delivery_requests = [(2, 3, 1, 0, 10)]
        vehicle_capacity = 1
        charging_stations = [1, 3]
        vehicle_battery_capacity = 10
        battery_consumption_rate = 1
        charging_time_per_unit = 1

        routes = solve(
            N, M, graph, vehicle_start_locations, delivery_requests,
            vehicle_capacity, charging_stations, vehicle_battery_capacity,
            battery_consumption_rate, charging_time_per_unit
        )
        # Validate structure of routes
        self.validate_route(routes, vehicle_start_locations)
        # Validate that each delivery request is properly covered
        self.validate_delivery_coverage(routes, delivery_requests)

    def test_multiple_vehicles_multiple_requests(self):
        # Construct a small graph with 5 nodes
        graph = {
            1: [(2, 2), (3, 5)],
            2: [(4, 3)],
            3: [(4, 2), (5, 4)],
            4: [(5, 1)],
            5: []
        }
        N = 2
        M = 3
        vehicle_start_locations = [1, 3]
        delivery_requests = [
            # (pickup_node, dropoff_node, package_size, time_window_start, time_window_end)
            (2, 5, 1, 0, 15),
            (3, 4, 1, 5, 20),
            (4, 5, 1, 10, 25)
        ]
        vehicle_capacity = 2
        charging_stations = [1, 5]
        vehicle_battery_capacity = 15
        battery_consumption_rate = 1
        charging_time_per_unit = 2

        routes = solve(
            N, M, graph, vehicle_start_locations, delivery_requests,
            vehicle_capacity, charging_stations, vehicle_battery_capacity,
            battery_consumption_rate, charging_time_per_unit
        )
        self.validate_route(routes, vehicle_start_locations)
        self.validate_delivery_coverage(routes, delivery_requests)

    def test_time_window_and_capacity(self):
        # Graph with cycles and multiple paths
        graph = {
            1: [(2, 3), (3, 4)],
            2: [(4, 2), (3, 2)],
            3: [(4, 2), (2, 1)],
            4: [(1, 5)]
        }
        N = 2
        M = 2
        vehicle_start_locations = [1, 2]
        delivery_requests = [
            # Tight time windows to force careful scheduling of pickup and dropoff
            (2, 4, 1, 3, 12),
            (3, 4, 1, 4, 10)
        ]
        vehicle_capacity = 1
        charging_stations = [1, 4]
        vehicle_battery_capacity = 10
        battery_consumption_rate = 1
        charging_time_per_unit = 1

        routes = solve(
            N, M, graph, vehicle_start_locations, delivery_requests,
            vehicle_capacity, charging_stations, vehicle_battery_capacity,
            battery_consumption_rate, charging_time_per_unit
        )
        self.validate_route(routes, vehicle_start_locations)
        self.validate_delivery_coverage(routes, delivery_requests)

    def test_charging_requirement(self):
        # Create a graph where charging is necessary to complete the route.
        graph = {
            1: [(2, 4)],
            2: [(3, 4)],
            3: [(4, 4)],
            4: []
        }
        N = 1
        M = 1
        vehicle_start_locations = [1]
        delivery_requests = [
            (2, 4, 1, 0, 20)
        ]
        vehicle_capacity = 1
        charging_stations = [1, 3]
        vehicle_battery_capacity = 8  # Not enough to go from 1 to 4 directly
        battery_consumption_rate = 1
        charging_time_per_unit = 2

        routes = solve(
            N, M, graph, vehicle_start_locations, delivery_requests,
            vehicle_capacity, charging_stations, vehicle_battery_capacity,
            battery_consumption_rate, charging_time_per_unit
        )
        self.validate_route(routes, vehicle_start_locations)
        self.validate_delivery_coverage(routes, delivery_requests)
        # Additional check: The route should contain at least one "charge" action if battery is tight.
        charging_found = any(instr[2] == "charge" for route in routes for instr in route)
        self.assertTrue(charging_found, "The route should include at least one charging action due to battery constraints.")

if __name__ == "__main__":
    unittest.main()