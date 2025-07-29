import unittest
from dynamic_vrp import solve

class TestDynamicVRP(unittest.TestCase):
    def test_single_depot_single_customer(self):
        # One depot and one customer; no dynamic events.
        depots = [
            # (depot_id, x, y, num_vehicles, vehicle_capacity, vehicle_cost_per_distance, start_time_window_start, start_time_window_end)
            (0, 0, 0, 1, 100, 1.0, 0, 1000)
        ]
        customers = [
            # (customer_id, x, y, demand, service_time_window_start, service_time_window_end)
            (101, 10, 0, 10, 0, 1000)
        ]
        # Distance matrix (2x2) where index 0 is depot and index 1 is customer.
        distance_matrix = [
            [0.0, 10.0],
            [10.0, 0.0]
        ]
        dynamic_events = []  # No dynamic events.
        # Expected route: Depot -> Customer -> Depot = 10 + 10 = 20.0 total cost.
        expected_cost = 20.0
        result = solve(depots, customers, distance_matrix, dynamic_events)
        self.assertAlmostEqual(result, expected_cost, places=5)

    def test_two_depot_two_customers(self):
        # Two depots and two customers; no dynamic events.
        depots = [
            (0, 0, 0, 1, 50, 1.0, 0, 100),
            (1, 100, 0, 1, 50, 1.0, 0, 100)
        ]
        customers = [
            (101, 10, 0, 20, 0, 100),
            (102, 90, 0, 20, 0, 100)
        ]
        # Distance matrix (4x4): indices: 0-depot0, 1-depot1, 2-customer101, 3-customer102.
        distance_matrix = [
            [0.0, 100.0, 10.0, 90.0],
            [100.0, 0.0, 90.0, 10.0],
            [10.0, 90.0, 0.0, 80.0],
            [90.0, 10.0, 80.0, 0.0]
        ]
        dynamic_events = []
        # Expected optimal: depot0 -> customer101 -> depot0 (10+10) and depot1 -> customer102 -> depot1 (10+10) = total 40.
        expected_cost = 40.0
        result = solve(depots, customers, distance_matrix, dynamic_events)
        self.assertAlmostEqual(result, expected_cost, places=5)

    def test_with_dynamic_event(self):
        # One depot with one initial customer and one dynamic event.
        depots = [
            (0, 0, 0, 1, 100, 1.0, 0, 100)
        ]
        customers = [
            (101, 10, 0, 20, 0, 100)
        ]
        # Add a dynamic demand event: new customer appears.
        dynamic_events = [
            # (arrival_time, customer_id, x_coordinate, y_coordinate, demand, service_time_window_start, service_time_window_end)
            (30, 102, 20, 0, 20, 50, 150)
        ]
        # Distance matrix (3x3): indices: 0-depot, 1-initial customer101, 2-dynamic customer102.
        distance_matrix = [
            [0.0, 10.0, 20.0],
            [10.0, 0.0, 10.0],
            [20.0, 10.0, 0.0]
        ]
        # Expected optimal route with dynamic event:
        # Either: Depot -> customer101 -> customer102 -> Depot = 10 + 10 + 20 = 40.0
        expected_cost = 40.0
        result = solve(depots, customers, distance_matrix, dynamic_events)
        self.assertAlmostEqual(result, expected_cost, places=5)

if __name__ == '__main__':
    unittest.main()