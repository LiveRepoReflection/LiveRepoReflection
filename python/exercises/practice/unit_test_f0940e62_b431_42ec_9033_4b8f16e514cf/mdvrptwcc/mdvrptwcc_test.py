import math
import unittest

from mdvrptwcc import solve_depot_routing

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

class TestMDVRPTWCC(unittest.TestCase):
    def validate_routes(self, depots, customers, vehicle_capacity, vehicle_speed, routes):
        # Create lookup dictionaries for quick access
        depot_lookup = {d['id']: d for d in depots}
        customer_lookup = {c['id']: c for c in customers}
        served_customers = set()
        
        # Validate each route
        for route in routes:
            depot_id, customer_ids = route
            self.assertIn(depot_id, depot_lookup, f"Depot {depot_id} not in depots list")
            depot = depot_lookup[depot_id]
            
            # Check that route does not assign more vehicles than available
            # (This will be validated across all routes later)
            total_demand = 0
            current_time = 0.0
            # Start at depot location
            current_x, current_y = depot['x'], depot['y']
            for cid in customer_ids:
                self.assertIn(cid, customer_lookup, f"Customer {cid} not in customers list")
                if cid in served_customers:
                    self.fail(f"Customer {cid} served multiple times")
                served_customers.add(cid)
                
                customer = customer_lookup[cid]
                # Update total demand for capacity check
                total_demand += customer['demand']
                self.assertLessEqual(total_demand, vehicle_capacity, 
                             f"Route from depot {depot_id} exceeds vehicle capacity")
                
                # Calculate travel time from current position to customer
                travel_time = euclidean_distance(current_x, current_y, customer['x'], customer['y']) / vehicle_speed
                arrival_time = current_time + travel_time
                # Wait if arriving before window starts
                if arrival_time < customer['tw_start']:
                    arrival_time = customer['tw_start']
                # Check time window constraint
                self.assertLessEqual(arrival_time, customer['tw_end'], 
                             f"Customer {cid} not served within time window; arrived at {arrival_time} but window ends at {customer['tw_end']}")
                # Service is assumed instantaneous; update time and position
                current_time = arrival_time
                current_x, current_y = customer['x'], customer['y']
            
            # Return to depot (optional check, can be used to calculate total travel time if needed)
            travel_back = euclidean_distance(current_x, current_y, depot['x'], depot['y']) / vehicle_speed
            # Total route time not specifically constrained but simulation ensures touring is consistent
        
        # Check that all customers have been served
        self.assertEqual(set(customer_lookup.keys()), served_customers, 
                         "Not all customers were served exactly once")
        
        # Validate that for each depot, number of routes does not exceed available vehicles
        depot_route_count = {}
        for route in routes:
            depot_id, _ = route
            depot_route_count[depot_id] = depot_route_count.get(depot_id, 0) + 1
        for depot in depots:
            used = depot_route_count.get(depot['id'], 0)
            self.assertLessEqual(used, depot['num_vehicles'], 
                                 f"Depot {depot['id']} used {used} vehicles which exceeds available {depot['num_vehicles']}")

    def test_single_depot_single_customer(self):
        depots = [
            {"id": 1, "x": 0, "y": 0, "num_vehicles": 1}
        ]
        customers = [
            {"id": 101, "x": 1, "y": 1, "demand": 5, "tw_start": 0, "tw_end": 10}
        ]
        vehicle_capacity = 10
        vehicle_speed = 1
        routes = solve_depot_routing(depots, customers, vehicle_capacity, vehicle_speed)
        # Check output format: list of routes, each route is a tuple (depot_id, [list of customer ids])
        self.assertIsInstance(routes, list)
        for route in routes:
            self.assertIsInstance(route, tuple)
            self.assertEqual(len(route), 2)
            depot_id, customer_ids = route
            self.assertIsInstance(depot_id, int)
            self.assertIsInstance(customer_ids, list)
        self.validate_routes(depots, customers, vehicle_capacity, vehicle_speed, routes)

    def test_multi_depot_multiple_customers(self):
        depots = [
            {"id": 1, "x": 0, "y": 0, "num_vehicles": 1},
            {"id": 2, "x": 10, "y": 10, "num_vehicles": 1}
        ]
        customers = [
            {"id": 101, "x": 1, "y": 1, "demand": 3, "tw_start": 0, "tw_end": 20},
            {"id": 102, "x": 2, "y": 2, "demand": 4, "tw_start": 0, "tw_end": 20},
            {"id": 103, "x": 8, "y": 8, "demand": 4, "tw_start": 0, "tw_end": 20}
        ]
        vehicle_capacity = 7
        vehicle_speed = 1
        routes = solve_depot_routing(depots, customers, vehicle_capacity, vehicle_speed)
        self.validate_routes(depots, customers, vehicle_capacity, vehicle_speed, routes)

    def test_time_window_constraints(self):
        depots = [
            {"id": 1, "x": 0, "y": 0, "num_vehicles": 1}
        ]
        customers = [
            {"id": 101, "x": 5, "y": 0, "demand": 5, "tw_start": 10, "tw_end": 15},
            {"id": 102, "x": 6, "y": 0, "demand": 5, "tw_start": 20, "tw_end": 25}
        ]
        vehicle_capacity = 10
        vehicle_speed = 1
        routes = solve_depot_routing(depots, customers, vehicle_capacity, vehicle_speed)
        self.validate_routes(depots, customers, vehicle_capacity, vehicle_speed, routes)

    def test_large_instance(self):
        # Create a larger instance with multiple depots and customers to test efficiency and correctness
        depots = [
            {"id": 1, "x": 0,  "y": 0,  "num_vehicles": 2},
            {"id": 2, "x": 50, "y": 50, "num_vehicles": 2}
        ]
        customers = []
        # Create 20 customers around each depot
        customer_id = 1000
        for depot in depots:
            for i in range(20):
                angle = (2 * math.pi * i) / 20
                x = depot["x"] + 5 * math.cos(angle)
                y = depot["y"] + 5 * math.sin(angle)
                # Set time window to be large enough so waiting is minimal
                customers.append({
                    "id": customer_id,
                    "x": round(x, 2),
                    "y": round(y, 2),
                    "demand": 1,
                    "tw_start": 0,
                    "tw_end": 100
                })
                customer_id += 1
        vehicle_capacity = 15
        vehicle_speed = 1
        routes = solve_depot_routing(depots, customers, vehicle_capacity, vehicle_speed)
        self.validate_routes(depots, customers, vehicle_capacity, vehicle_speed, routes)

if __name__ == '__main__':
    unittest.main()