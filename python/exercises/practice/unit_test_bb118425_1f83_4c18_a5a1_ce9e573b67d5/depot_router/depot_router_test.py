import unittest
from depot_router import optimize_routes

class TestDepotRouter(unittest.TestCase):
    def validate_solution(self, routes, num_customers, depots, customers):
        # Check that the output routes is a list of tuples (depot_index, [customer_indices])
        visited_customers = set()
        total_vehicle_count = sum(d[2] for d in depots)
        self.assertLessEqual(len(routes), total_vehicle_count, "More routes returned than available vehicles.")

        for route in routes:
            self.assertIsInstance(route, tuple, "Each route should be a tuple (depot_index, route_list)")
            self.assertEqual(len(route), 2, "Each tuple must have exactly two elements")
            depot_index, cust_route = route
            self.assertIsInstance(depot_index, int, "Depot index must be an integer")
            self.assertTrue(0 <= depot_index < len(depots), "Depot index out of range")
            self.assertIsInstance(cust_route, list, "Route should be a list of customer indices")
            for cust_idx in cust_route:
                self.assertIsInstance(cust_idx, int, "Customer indices should be integers")
                self.assertTrue(0 <= cust_idx < num_customers, "Customer index out of range")
                self.assertIn(depot_index, customers[cust_idx][6], 
                              f"Customer {cust_idx} cannot be served by depot {depot_index} per depot preference")
                self.assertNotIn(cust_idx, visited_customers, "Each customer must be visited exactly once")
                visited_customers.add(cust_idx)

        # Check that all customers are visited exactly once
        self.assertEqual(visited_customers, set(range(num_customers)),
                         "Not all customers have been visited exactly once.")

    def test_simple_instance(self):
        # Single depot with two vehicles and two customers
        depots = [
            (37.7749, -122.4194, 2, 480)  # (lat, lon, num_vehicles, resource_capacity)
        ]
        customers = [
            (37.7833, -122.4094, 10, 60, 120, 15, [0]),  # Customer 0: allowed depot 0 only
            (37.7937, -122.3962, 20, 180, 240, 30, [0])   # Customer 1: allowed depot 0 only
        ]
        # Distance matrix dimensions: 1 depot + 2 customers = 3 x 3 matrix
        distance_matrix = [
            [0,   10, 15],
            [10,  0,   8],
            [15,  8,   0]
        ]
        vehicle_capacity = 30
        max_route_duration = 400

        routes = optimize_routes(depots, customers, distance_matrix, vehicle_capacity, max_route_duration)
        self.validate_solution(routes, len(customers), depots, customers)

    def test_complex_instance(self):
        # Two depots with two vehicles each and four customers.
        depots = [
            (37.7749, -122.4194, 2, 480),  # Depot 0
            (37.8044, -122.2711, 2, 480)   # Depot 1
        ]
        customers = [
            (37.7833, -122.4094, 10, 60, 120, 15, [0]),        # Customer 0: can be served only by depot 0
            (37.7937, -122.3962, 20, 150, 210, 30, [0, 1]),      # Customer 1: can be served by depot 0 or 1
            (37.7890, -122.4000, 15, 80, 140, 20, [1]),          # Customer 2: can be served only by depot 1
            (37.8000, -122.4100, 5, 200, 260, 15, [1, 0])         # Customer 3: can be served by depot 1 or 0
        ]
        # Distance matrix dimensions: 2 depots + 4 customers = 6 x 6 matrix
        # Indices 0-1: depots, 2-5: customers
        distance_matrix = [
            [0, 12, 10, 20, 25, 30],  # Depot 0 to [Depot0, Depot1, Cust0, Cust1, Cust2, Cust3]
            [12, 0, 15, 10, 20, 22],  # Depot 1
            [10, 15, 0, 8, 12, 14],   # Customer 0
            [20, 10, 8, 0, 5, 7],     # Customer 1
            [25, 20, 12, 5, 0, 3],    # Customer 2
            [30, 22, 14, 7, 3, 0]     # Customer 3
        ]
        vehicle_capacity = 30
        max_route_duration = 300

        routes = optimize_routes(depots, customers, distance_matrix, vehicle_capacity, max_route_duration)
        self.validate_solution(routes, len(customers), depots, customers)

    def test_no_solution_due_to_capacity(self):
        # Test instance where one customer's demand exceed any vehicle's capacity.
        depots = [
            (37.7749, -122.4194, 1, 480)
        ]
        customers = [
            (37.7833, -122.4094, 40, 60, 120, 15, [0])  # demand exceeds vehicle capacity (which will be set to 30)
        ]
        distance_matrix = [
            [0, 10],
            [10, 0]
        ]
        vehicle_capacity = 30
        max_route_duration = 400

        # In this unsolvable instance, we expect the solution to either return an empty route list
        # or raise an exception indicating no valid solution is possible.
        try:
            routes = optimize_routes(depots, customers, distance_matrix, vehicle_capacity, max_route_duration)
            # If routes are returned, then no customer should be scheduled.
            # Depending on implementation, a valid approach might return an empty list.
            self.assertTrue(len(routes) == 0 or all(len(route[1]) == 0 for route in routes),
                            "Routes should be empty if no valid solution exists due to capacity constraints")
        except Exception:
            pass  # An exception is acceptable for unsolvable cases

if __name__ == '__main__':
    unittest.main()