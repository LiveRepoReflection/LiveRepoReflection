import math
import unittest
from multi_depot_routing import plan_routes

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def compute_route_schedule(route, depot_location, delivery_dict, distance_matrix, depot_index, vehicle_speed, service_time, depot_indices_offset):
    """
    Given a route (list of integers, where first and last are depot id),
    compute the arrival times at each delivery location.
    We'll simulate the schedule by assuming:
      - The vehicle departs depot at time 0.
      - Travel time between points = distance (from matrix or computed from coordinates) / vehicle_speed.
      - At each delivery, add service_time.
    Returns a list of arrival times at each point on the route (including the depot start, deliveries, and depot return).
    """
    schedule = [0]
    # Get the last location index in our distance matrix indices.
    # For depots, indices: 0 ... (num_depots - 1)
    # For deliveries, indices: depot_indices_offset ... end
    # Map depot id to depot index and deliveries id to index will be passed externally.
    # However, for testing, we rely on the provided distance_matrix directly using computed indices.
    # Here we assume that depot_location and delivery_dict provide the mapping.
    indices = []
    # First, find depot index corresponding to current route's depot id
    # Note: depot_ids are assumed to match with the order in the depots list
    depot_idx = depot_index[route[0]]
    indices.append(depot_idx)
    for req_id in route[1:-1]:
        indices.append(delivery_dict[req_id]['matrix_index'])
    # End depot index same as start depot.
    indices.append(depot_idx)
    
    # Calculate cumulative arrival times using distance_matrix if available.
    for i in range(len(indices) - 1):
        travel_time = distance_matrix[indices[i]][indices[i+1]] / vehicle_speed
        # add current travel time plus waiting time if needed to meet the next delivery's time window
        arrival = schedule[-1] + travel_time
        if i+1 < len(indices) - 1:
            # For a delivery, if arrival is before start_time, wait until start_time.
            start_time = delivery_dict[ route[i+1] ]['time_window'][0]
            if arrival < start_time:
                arrival = start_time
            # Add service time
            arrival += service_time
        schedule.append(arrival)
    return schedule

class TestMultiDepotRouting(unittest.TestCase):
    def setUp(self):
        # Create a standard distance matrix calculator for testing purposes.
        # We will compute Euclidean distances based on locations.
        self.vehicle_speed = 1  # km per minute for simplicity.
        self.service_time = 2   # minutes service time.
    
    def build_distance_matrix(self, depot_locations, delivery_locations):
        # Build a matrix where first len(depot_locations) indices correspond to depots,
        # and subsequent indices for delivery locations.
        all_locations = depot_locations + delivery_locations
        n = len(all_locations)
        matrix = [[0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                matrix[i][j] = euclidean_distance(all_locations[i], all_locations[j])
        return matrix

    def validate_routes(self, depots, delivery_requests, distance_matrix, vehicle_speed, service_time, routes):
        """
        Validate that:
          - Each route starts and ends with the same depot.
          - Every delivery request is served exactly once.
          - Capacity constraints at each route are not exceeded.
          - Time window constraints are met.
          - The number of routes per depot does not exceed available vehicles.
        """
        served = set()
        depot_route_count = {}
        # Build mappings for depots and deliveries for ease of access.
        depot_index = {}
        depot_locations = []
        for idx, d in enumerate(depots):
            depot_id, capacity, vehicles, location = d
            depot_index[depot_id] = idx
            depot_locations.append(location)
            depot_route_count[depot_id] = 0
        
        delivery_dict = {}
        delivery_locations = []
        for d_idx, r in enumerate(delivery_requests):
            request_id, package_size, time_window, location = r
            delivery_dict[request_id] = {'package_size': package_size, 'time_window': time_window, 'location': location, 
                                         'matrix_index': len(depot_locations) + d_idx}
            delivery_locations.append(location)
        
        # For each route, check constraints.
        for route in routes:
            # Route must be non-empty and have at least depot, one delivery, depot.
            self.assertTrue(len(route) >= 3, "Route must contain depot, at least one delivery, and depot return")
            depot_id = route[0]
            self.assertEqual(route[0], route[-1], "Route must start and end at the same depot")
            self.assertIn(depot_id, depot_index, "Route should start with a valid depot id")
            depot_route_count[depot_id] += 1
            # Check that deliveries in this route do not exceed capacity.
            # Find the depot capacity corresponding to the depot_id.
            depot_cap = None
            for d in depots:
                if d[0] == depot_id:
                    depot_cap = d[1]
                    break
            self.assertIsNotNone(depot_cap, "Depot capacity should be defined")
            total_load = 0
            for req_id in route[1:-1]:
                self.assertIn(req_id, delivery_dict, "Delivery request id must be valid")
                total_load += delivery_dict[req_id]['package_size']
                self.assertNotIn(req_id, served, "Delivery should not be served more than once")
                served.add(req_id)
            
            self.assertLessEqual(total_load, depot_cap, "Total packages in route exceed depot capacity")
            
            # Validate time window constraints using the distance matrix.
            schedule = compute_route_schedule(route, depot_locations[depot_index[depot_id]], delivery_dict, 
                                              distance_matrix, depot_index, vehicle_speed, service_time,
                                              depot_indices_offset=len(depot_locations))
            # For each delivery, check arrival time is within time window.
            # schedule indices: 0 -> depot start, 1 -> first delivery, ..., last -> depot return.
            for idx, req_id in enumerate(route[1:-1], start=1):
                arrival_time = schedule[idx] - service_time  # arrival time before service
                tw_start, tw_end = delivery_dict[req_id]['time_window']
                self.assertGreaterEqual(arrival_time, tw_start, "Arrival time is before time window start")
                self.assertLessEqual(arrival_time, tw_end, "Arrival time is after time window end")
        
        # Ensure every delivery is served exactly once.
        self.assertEqual(set(delivery_dict.keys()), served, "Not all deliveries are served exactly once")
        # Check vehicle limit per depot.
        for d in depots:
            depot_id, capacity, vehicles, location = d
            self.assertLessEqual(depot_route_count[depot_id], vehicles, "Number of routes exceed available vehicles for depot")

    def test_empty_delivery_requests(self):
        depots = [(1, 10, 2, (0, 0))]
        delivery_requests = []
        depot_locations = [d[3] for d in depots]
        delivery_locations = []
        distance_matrix = self.build_distance_matrix(depot_locations, delivery_locations)
        routes = plan_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time)
        self.assertEqual(routes, [], "Expected no routes when there are no delivery requests")

    def test_single_depot_single_delivery(self):
        depots = [(1, 10, 1, (0, 0))]
        delivery_requests = [
            (101, 5, (0, 20), (3, 4))
        ]
        depot_locations = [d[3] for d in depots]
        delivery_locations = [r[3] for r in delivery_requests]
        distance_matrix = self.build_distance_matrix(depot_locations, delivery_locations)
        routes = plan_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time)
        # Validate that one route is returned
        self.assertEqual(len(routes), 1, "Expected one route for single delivery")
        # Validate the route structure and constraints.
        self.validate_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time, routes)

    def test_single_depot_multiple_deliveries(self):
        depots = [(1, 10, 2, (0, 0))]
        delivery_requests = [
            (101, 3, (0, 30), (1, 2)),
            (102, 4, (5, 35), (2, 1)),
            (103, 2, (10, 40), (3, 3))
        ]
        depot_locations = [d[3] for d in depots]
        delivery_locations = [r[3] for r in delivery_requests]
        distance_matrix = self.build_distance_matrix(depot_locations, delivery_locations)
        routes = plan_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time)
        # Validate that all delivery requests are served properly.
        self.validate_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time, routes)

    def test_multiple_depots(self):
        depots = [
            (1, 8, 1, (0, 0)),
            (2, 15, 2, (10, 10))
        ]
        delivery_requests = [
            (101, 4, (0, 25), (1, 1)),
            (102, 3, (5, 30), (2, 2)),
            (103, 5, (10, 35), (11, 11)),
            (104, 7, (15, 50), (12, 12))
        ]
        depot_locations = [d[3] for d in depots]
        delivery_locations = [r[3] for r in delivery_requests]
        distance_matrix = self.build_distance_matrix(depot_locations, delivery_locations)
        routes = plan_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time)
        self.validate_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time, routes)

    def test_tight_time_windows(self):
        # In this case, deliveries have very tight time windows forcing waiting times.
        depots = [(1, 10, 2, (0, 0))]
        delivery_requests = [
            (101, 2, (5, 6), (3, 4)),
            (102, 3, (10, 12), (6, 8))
        ]
        depot_locations = [d[3] for d in depots]
        delivery_locations = [r[3] for r in delivery_requests]
        distance_matrix = self.build_distance_matrix(depot_locations, delivery_locations)
        routes = plan_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time)
        self.validate_routes(depots, delivery_requests, distance_matrix, self.vehicle_speed, self.service_time, routes)

if __name__ == '__main__':
    unittest.main()