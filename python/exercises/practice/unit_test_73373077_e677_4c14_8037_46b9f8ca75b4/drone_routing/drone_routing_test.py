import unittest
import math
from drone_routing import plan_routes

def euclidean_distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

class DroneRoutingTest(unittest.TestCase):
    def validate_route_structure(self, routes, num_drones):
        # Check routes is a list of length num_drones and each route is a list of tuples
        self.assertIsInstance(routes, list, "Routes should be a list")
        self.assertEqual(len(routes), num_drones, f"Routes should list {num_drones} drones")
        for route in routes:
            self.assertIsInstance(route, list, "Each drone route should be a list")
            for step in route:
                self.assertEqual(len(step), 3, "Each route step must be a tuple of (location_type, id, time_of_arrival)")
                location_type, identifier, time_of_arrival = step
                self.assertIn(location_type, ["depot", "delivery"], "Location type must be either 'depot' or 'delivery'")
                self.assertIsInstance(identifier, int, "Identifier must be an integer")
                self.assertIsInstance(time_of_arrival, int, "time_of_arrival must be an integer")
    
    def validate_increasing_times(self, route):
        # Ensure time_of_arrival in the route is non-decreasing
        times = [step[2] for step in route]
        self.assertEqual(times, sorted(times), "Times in the route should be non-decreasing")

    def test_empty_deliveries(self):
        # When no deliveries are provided, expect that each drone only visits the depot
        num_drones = 3
        depot_location = (0, 0)
        drone_battery_capacity = 50
        drone_package_capacity = 1
        battery_consumption_rate = 1
        delivery_requests = []
        time_penalty_per_unit = 1
        missed_delivery_penalty = 1000
        charging_time_per_unit = 1
        max_simulation_time = 100
        
        routes = plan_routes(
            num_drones,
            depot_location,
            drone_battery_capacity,
            drone_package_capacity,
            battery_consumption_rate,
            delivery_requests,
            time_penalty_per_unit,
            missed_delivery_penalty,
            charging_time_per_unit,
            max_simulation_time
        )
        self.validate_route_structure(routes, num_drones)
        for route in routes:
            # Each route should contain at least one step visiting depot.
            self.assertGreaterEqual(len(route), 1, "Each route should have at least one depot visit")
            for step in route:
                self.assertEqual(step[0], "depot", "Since there are no deliveries, only depot visits are allowed")
            self.validate_increasing_times(route)

    def test_single_delivery(self):
        # Single delivery: one drone should perform delivery within its time window if possible.
        num_drones = 1
        depot_location = (0, 0)
        drone_battery_capacity = 100
        drone_package_capacity = 2
        battery_consumption_rate = 1
        # Request: (id, x, y, start_time, end_time, package_weight)
        delivery_requests = [
            (1, 10, 0, 5, 20, 1)
        ]
        time_penalty_per_unit = 1
        missed_delivery_penalty = 1000
        charging_time_per_unit = 1
        max_simulation_time = 50

        routes = plan_routes(
            num_drones,
            depot_location,
            drone_battery_capacity,
            drone_package_capacity,
            battery_consumption_rate,
            delivery_requests,
            time_penalty_per_unit,
            missed_delivery_penalty,
            charging_time_per_unit,
            max_simulation_time
        )
        self.validate_route_structure(routes, num_drones)
        route = routes[0]
        self.validate_increasing_times(route)
        # Check if delivery is served properly; if delivered, it should be within [start_time, end_time]
        delivered = False
        for step in route:
            if step[0] == "delivery":
                delivered = True
                request_id = step[1]
                time_arrival = step[2]
                # Find corresponding request details
                req = next((r for r in delivery_requests if r[0] == request_id), None)
                self.assertIsNotNone(req, "Delivery request ID should match one from input")
                start_time, end_time = req[3], req[4]
                self.assertGreaterEqual(time_arrival, start_time, "Delivery should not occur before the time window")
                self.assertLessEqual(time_arrival, end_time, "Delivery should occur within the time window")
        # It is acceptable if no delivery was performed as long as planning constraints are met.

    def test_multiple_deliveries(self):
        # Multiple deliveries with two drones. Various feasibility with time windows and battery constraint.
        num_drones = 2
        depot_location = (0, 0)
        drone_battery_capacity = 150
        drone_package_capacity = 2
        battery_consumption_rate = 2
        delivery_requests = [
            (1, 20, 10, 10, 40, 1),
            (2, 15, -5, 5, 30, 1),
            (3, -10, -10, 20, 50, 1),
            (4, -5, 20, 25, 60, 1),
            (5, 30, 15, 15, 45, 1)
        ]
        time_penalty_per_unit = 1
        missed_delivery_penalty = 500
        charging_time_per_unit = 1
        max_simulation_time = 80

        routes = plan_routes(
            num_drones,
            depot_location,
            drone_battery_capacity,
            drone_package_capacity,
            battery_consumption_rate,
            delivery_requests,
            time_penalty_per_unit,
            missed_delivery_penalty,
            charging_time_per_unit,
            max_simulation_time
        )
        self.validate_route_structure(routes, num_drones)
        
        served_requests = set()
        for route in routes:
            self.validate_increasing_times(route)
            last_location = depot_location
            last_time = None
            for step in route:
                loc_type, identifier, time_arrival = step
                self.assertIsInstance(time_arrival, int, "Time arrival must be an integer")
                if last_time is not None:
                    self.assertGreaterEqual(time_arrival, last_time, "Time should be non-decreasing between steps")
                last_time = time_arrival
                if loc_type == "delivery":
                    # Verify that the delivery is among the given requests
                    req = next((r for r in delivery_requests if r[0] == identifier), None)
                    self.assertIsNotNone(req, "Delivery ID in route must match an input request")
                    # Check time window constraints if possible
                    start_time, end_time = req[3], req[4]
                    self.assertGreaterEqual(time_arrival, start_time, "Delivery should not occur before its time window")
                    self.assertLessEqual(time_arrival, end_time, "Delivery should occur within its time window")
                    served_requests.add(identifier)
                # Check battery feasibility if possible based on consumption rate.
                # Calculate distance from last location to current location.
                current_location = depot_location if loc_type == "depot" else (next(r for r in delivery_requests if r[0]==identifier)[1:3])
                dist = euclidean_distance(last_location, current_location)
                battery_usage = dist * battery_consumption_rate
                self.assertTrue(battery_usage <= drone_battery_capacity, "Each leg must be within battery capacity")
                last_location = current_location

        # Ensure that served deliveries are a subset of the input requests.
        input_request_ids = set(req[0] for req in delivery_requests)
        self.assertTrue(served_requests.issubset(input_request_ids), "Served requests must be a subset of input requests")
    
if __name__ == '__main__':
    unittest.main()