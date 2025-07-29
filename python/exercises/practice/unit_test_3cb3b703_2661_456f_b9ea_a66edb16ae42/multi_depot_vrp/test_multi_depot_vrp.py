import unittest
import math
from multi_depot_vrp import solve_vrp

class TestMultiDepotVRP(unittest.TestCase):
    def simulate_route(self, depot, route, depot_index, travel_time_matrix, num_depots, customers):
        time = 0.0
        current_index = depot_index  # depot index in the travel_time_matrix
        for customer_id in route:
            customer_index = num_depots + customer_id  # customer's index in travel_time_matrix
            time += travel_time_matrix[current_index][customer_index]
            cust = customers[customer_id]
            if time < cust['time_window_start']:
                time = cust['time_window_start']
            self.assertLessEqual(
                time, cust['time_window_end'],
                f"Time window violated for customer {customer_id} in route {route}"
            )
            current_index = customer_index
        # Return to depot
        time += travel_time_matrix[current_index][depot_index]
        return time

    def test_single_depot_single_customer(self):
        # One depot and one customer.
        depots = [
            {"location": (0, 0), "vehicle_count": 1, "vehicle_capacity": 10}
        ]
        customers = [
            {"location": (1, 1), "demand": 5, "time_window_start": 0, "time_window_end": 20}
        ]

        def euclidean(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        locations = [depots[0]['location']] + [customers[i]['location'] for i in range(len(customers))]
        n = len(locations)
        travel_time_matrix = [[euclidean(locations[i], locations[j]) for j in range(n)] for i in range(n)]

        result = solve_vrp(depots, customers, travel_time_matrix)

        total_customers_served = sum(len(depot_routes['routes'][i]) for depot_routes in result for i in range(len(depot_routes['routes'])))
        self.assertEqual(total_customers_served, len(customers), "Not all customers are served.")

        for depot_routes in result:
            depot_id = depot_routes['depot_id']
            depot_info = depots[depot_id]
            self.assertLessEqual(
                len(depot_routes['routes']),
                depot_info['vehicle_count'],
                f"Depot {depot_id} exceeds available vehicle count."
            )
            for route in depot_routes['routes']:
                total_demand = sum(customers[c]['demand'] for c in route)
                self.assertLessEqual(
                    total_demand, depot_info['vehicle_capacity'],
                    f"Capacity constraint violated in depot {depot_id} for route {route}."
                )
                self.simulate_route(depot_info, route, depot_id, travel_time_matrix, len(depots), customers)

    def test_multiple_depots_multiple_customers(self):
        # Two depots and multiple customers.
        depots = [
            {"location": (0, 0), "vehicle_count": 2, "vehicle_capacity": 15},
            {"location": (10, 10), "vehicle_count": 1, "vehicle_capacity": 10}
        ]
        customers = [
            {"location": (1, 1), "demand": 5, "time_window_start": 0, "time_window_end": 15},
            {"location": (2, 2), "demand": 6, "time_window_start": 5, "time_window_end": 20},
            {"location": (9, 9), "demand": 5, "time_window_start": 0, "time_window_end": 25},
            {"location": (8, 8), "demand": 4, "time_window_start": 10, "time_window_end": 30}
        ]

        def euclidean(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        locations = [d['location'] for d in depots] + [c['location'] for c in customers]
        n = len(locations)
        travel_time_matrix = [[euclidean(locations[i], locations[j]) for j in range(n)] for i in range(n)]

        result = solve_vrp(depots, customers, travel_time_matrix)

        served_customers = []
        for depot_routes in result:
            depot_id = depot_routes['depot_id']
            depot_info = depots[depot_id]
            self.assertLessEqual(
                len(depot_routes['routes']),
                depot_info['vehicle_count'],
                f"Depot {depot_id} exceeds available vehicle count."
            )
            for route in depot_routes['routes']:
                total_demand = sum(customers[c]['demand'] for c in route)
                self.assertLessEqual(
                    total_demand, depot_info['vehicle_capacity'],
                    f"Capacity constraint violated in depot {depot_id} for route {route}."
                )
                self.simulate_route(depot_info, route, depot_id, travel_time_matrix, len(depots), customers)
                served_customers.extend(route)

        self.assertCountEqual(
            served_customers, list(range(len(customers))),
            "Customers are not served exactly once."
        )

    def test_time_window_waiting(self):
        # Scenario that requires a vehicle to wait due to early arrival.
        depots = [
            {"location": (0, 0), "vehicle_count": 1, "vehicle_capacity": 20}
        ]
        customers = [
            {"location": (2, 0), "demand": 5, "time_window_start": 5, "time_window_end": 15},
            {"location": (4, 0), "demand": 5, "time_window_start": 10, "time_window_end": 20}
        ]

        def euclidean(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        locations = [depots[0]['location']] + [cust['location'] for cust in customers]
        n = len(locations)
        travel_time_matrix = [[euclidean(locations[i], locations[j]) for j in range(n)] for i in range(n)]

        result = solve_vrp(depots, customers, travel_time_matrix)

        for depot_routes in result:
            depot_id = depot_routes['depot_id']
            depot_info = depots[depot_id]
            for route in depot_routes['routes']:
                self.simulate_route(depot_info, route, depot_id, travel_time_matrix, len(depots), customers)

if __name__ == "__main__":
    unittest.main()