import unittest
import math
from depot_delivery import depot_delivery

class DepotDeliveryTest(unittest.TestCase):
    def setUp(self):
        # This helper function computes Euclidean distance as travel time (assuming speed = 1 unit distance per unit time)
        self.euclidean_distance = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
    
    def build_cost_matrix(self, locations):
        n = len(locations)
        matrix = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                matrix[i][j] = self.euclidean_distance(locations[i], locations[j])
        return matrix

    def test_empty_customers(self):
        # One depot, but no customers
        depots = [{
            "id": 0,
            "location": (0, 0),
            "num_vehicles": 2,
            "capacity": 10,
            "operating_hours": (0, 100)
        }]
        customers = []  # No customers.
        # Only one location from depot.
        locations = [depots[0]["location"]]
        cost_matrix = self.build_cost_matrix(locations)
        vehicle_speed = 1.0
        penalty_late = 5
        penalty_vehicle = 10

        result = depot_delivery(depots, customers, cost_matrix, vehicle_speed, penalty_late, penalty_vehicle)
        # Expecting an empty list of routes and total cost of 0 since no deliveries are needed.
        self.assertIsInstance(result, dict)
        self.assertIn("routes", result)
        self.assertIn("total_cost", result)
        self.assertEqual(len(result["routes"]), 0)
        self.assertEqual(result["total_cost"], 0)

    def test_single_customer_on_time(self):
        # One depot and one customer whose delivery can be on time.
        depots = [{
            "id": 0,
            "location": (0, 0),
            "num_vehicles": 1,
            "capacity": 10,
            "operating_hours": (0, 100)
        }]
        customers = [{
            "id": 1,
            "location": (3, 4),  # distance 5 from depot
            "demand": 5,
            "time_window": (10, 20),
            "service_time": 2
        }]
        # Locations order: depot, customer
        locations = [depots[0]["location"], customers[0]["location"]]
        cost_matrix = self.build_cost_matrix(locations)
        vehicle_speed = 1.0
        penalty_late = 5
        penalty_vehicle = 10

        result = depot_delivery(depots, customers, cost_matrix, vehicle_speed, penalty_late, penalty_vehicle)
        # Validate output structure
        self.assertIsInstance(result, dict)
        self.assertIn("routes", result)
        self.assertIn("total_cost", result)

        routes = result["routes"]
        self.assertGreaterEqual(len(routes), 1)
        # Each route should start and end at the depot
        for route in routes:
            self.assertIn("depot", route)
            self.assertIn("route", route)
            self.assertIn("demand", route)
            self.assertIn("travel_time", route)
            self.assertIn("penalty", route)
            self.assertEqual(route["route"][0], route["depot"])
            self.assertEqual(route["route"][-1], route["depot"])
        # Check that total delivered demand equals the customer demand.
        total_delivered = sum(route["demand"] for route in routes)
        self.assertEqual(total_delivered, customers[0]["demand"])
        # Since the customer time window is wide enough, penalty should be 0.
        self.assertEqual(sum(route["penalty"] for route in routes), 0)

    def test_split_delivery_required(self):
        # One depot, one customer with demand exceeding vehicle capacity.
        depots = [{
            "id": 0,
            "location": (0, 0),
            "num_vehicles": 2,
            "capacity": 7,  # capacity less than demand
            "operating_hours": (0, 200)
        }]
        customers = [{
            "id": 1,
            "location": (6, 8),  # distance 10
            "demand": 12,  # Exceeds single vehicle's capacity => must split across 2 vehicles.
            "time_window": (20, 40),
            "service_time": 3
        }]
        locations = [depots[0]["location"], customers[0]["location"]]
        cost_matrix = self.build_cost_matrix(locations)
        vehicle_speed = 1.0
        penalty_late = 10
        penalty_vehicle = 15

        result = depot_delivery(depots, customers, cost_matrix, vehicle_speed, penalty_late, penalty_vehicle)
        self.assertIsInstance(result, dict)
        self.assertIn("routes", result)
        routes = result["routes"]
        # Expecting two routes since one vehicle cannot cover all the demand.
        self.assertEqual(len(routes), 2)

        # Check that each route starts and ends at the depot.
        for route in routes:
            self.assertEqual(route["route"][0], route["depot"])
            self.assertEqual(route["route"][-1], route["depot"])
            # Each route's delivered demand should not exceed depot capacity.
            self.assertLessEqual(route["demand"], depots[0]["capacity"])
        
        # Total delivered demand should equal the customer demand.
        total_delivered = sum(route["demand"] for route in routes)
        self.assertEqual(total_delivered, customers[0]["demand"])

    def test_multiple_depots_customers(self):
        # Two depots, and two customers, to check route allocation.
        depots = [
            {
                "id": 0,
                "location": (0, 0),
                "num_vehicles": 1,
                "capacity": 10,
                "operating_hours": (0, 100)
            },
            {
                "id": 1,
                "location": (10, 0),
                "num_vehicles": 1,
                "capacity": 15,
                "operating_hours": (0, 100)
            }
        ]
        customers = [
            {
                "id": 2,
                "location": (2, 2),
                "demand": 8,
                "time_window": (5, 30),
                "service_time": 2
            },
            {
                "id": 3,
                "location": (8, 2),
                "demand": 10,
                "time_window": (10, 40),
                "service_time": 3
            }
        ]
        # Combine all locations: depots then customers.
        locations = [depots[0]["location"], depots[1]["location"], customers[0]["location"], customers[1]["location"]]
        cost_matrix = self.build_cost_matrix(locations)
        vehicle_speed = 1.0
        penalty_late = 20
        penalty_vehicle = 12

        result = depot_delivery(depots, customers, cost_matrix, vehicle_speed, penalty_late, penalty_vehicle)
        self.assertIsInstance(result, dict)
        self.assertIn("routes", result)
        routes = result["routes"]
        # There should be 2 routes since we have 2 depots and each should handle closer customer.
        self.assertEqual(len(routes), 2)

        # Verify each route has proper depot assignment
        depot_ids_used = set()
        total_delivered = 0
        for route in routes:
            self.assertIn(route["depot"], [depot["id"] for depot in depots])
            depot_ids_used.add(route["depot"])
            # Validate that route starts and ends at the assigned depot.
            self.assertEqual(route["route"][0], route["depot"])
            self.assertEqual(route["route"][-1], route["depot"])
            total_delivered += route["demand"]
        # Total delivered demands should match sum of customer demands.
        expected_total_demand = sum(customer["demand"] for customer in customers)
        self.assertEqual(total_delivered, expected_total_demand)
        # Optionally, check that both depots are used if geographically beneficial.
        self.assertEqual(len(depot_ids_used), 2)

    def test_time_window_penalty(self):
        # One depot, one customer with a time window that cannot be met.
        depots = [{
            "id": 0,
            "location": (0, 0),
            "num_vehicles": 1,
            "capacity": 20,
            "operating_hours": (0, 50)
        }]
        customers = [{
            "id": 1,
            "location": (30, 40),  # distance 50
            "demand": 10,
            "time_window": (10, 20),  # too short, cannot be met if travel is 50 time units.
            "service_time": 5
        }]
        locations = [depots[0]["location"], customers[0]["location"]]
        cost_matrix = self.build_cost_matrix(locations)
        vehicle_speed = 1.0  # travel time equals distance.
        penalty_late = 100
        penalty_vehicle = 10

        result = depot_delivery(depots, customers, cost_matrix, vehicle_speed, penalty_late, penalty_vehicle)
        self.assertIsInstance(result, dict)
        self.assertIn("routes", result)
        routes = result["routes"]
        self.assertEqual(len(routes), 1)
        # Check that penalty is incurred due to late delivery.
        self.assertGreater(routes[0]["penalty"], 0)

if __name__ == "__main__":
    unittest.main()